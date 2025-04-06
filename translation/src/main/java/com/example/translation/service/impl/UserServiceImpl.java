package com.example.translation.service.impl;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import com.aliyuncs.CommonRequest;
import com.aliyuncs.CommonResponse;
import com.aliyuncs.DefaultAcsClient;
import com.aliyuncs.IAcsClient;
import com.aliyuncs.exceptions.ClientException;
import com.aliyuncs.exceptions.ServerException;
import com.aliyuncs.http.MethodType;
import com.aliyuncs.profile.DefaultProfile;
import com.example.translation.common.config.AliyunConstant;
import com.example.translation.common.result.ResultData;
import com.example.translation.common.result.ReturnCode;
import com.example.translation.common.util.BaseUtil;
import com.example.translation.common.util.JwtUtil;
import com.example.translation.common.util.SnowflakeIdGenerator;
import com.example.translation.mapper.UserMapper;
import com.example.translation.pojo.dto.AliyunSms;
import com.example.translation.pojo.po.SmsLogin;
import com.example.translation.pojo.po.User;
import com.example.translation.pojo.vo.UserVO;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.serializer.StringRedisSerializer;
import org.springframework.stereotype.Service;
import java.util.HashMap;
import java.util.Map;
import java.util.Random;
import java.util.concurrent.TimeUnit;

@Service
public class UserServiceImpl implements com.example.translation.service.UserService {
    @Autowired
    private UserMapper userMapper;

    @Autowired
    private SnowflakeIdGenerator snowflakeIdGenerator;
    @Autowired
    private RedisTemplate<String, String> redisTemplate;
    private Random random = new Random();
    private static final String MOBILE_PATTERN = "^1[3-9]\\d{9}$";
    @Value("${aliyun.sms.access-key-id}")
    private String accessKeyId;

    @Value("${aliyun.sms.access-key-secret}")
    private String accessKeySecret;

    @Override
    public ResultData<String> registerUser(String username, String password) {
        if (userMapper.checkUsernameOrPasswordExists(username,password)> 0) {
            return ResultData.fail(ReturnCode.RC999.getCode(), "账号或密码已存在");
        }
        User user = new User();
        user.setId(snowflakeIdGenerator.nextId());
        user.setUsername(username);
        user.setPassword(password);
        user.setName(generateUniqueName());
        userMapper.insertUser(user);
        return ResultData.success("注册成功");
    }
    @Override
    public ResultData<UserVO>  login(String username, String password) {
        // 检查用户名和密码是否正确
        if (userMapper.checkUsernameAndPasswordExists(username, password) == 0) {
            return ResultData.fail(ReturnCode.USERNAME_OR_PASSWORD_ERROR.getCode(), ReturnCode.USERNAME_OR_PASSWORD_ERROR.getMessage());
        }
        User user = userMapper.findUserInfoByUsernameAndPassword(username, password);
        if (user == null) {
            return ResultData.fail(ReturnCode.RC999.getCode(), "用户不存在");
        }
        // 生成 token
        String token = JwtUtil.generateToken(user.getId(), user.getName());
        UserVO userVO =new UserVO();
        userVO.setName(user.getName());
        userVO.setAvatar(user.getAvatar());
        userVO.setToken(token);
        return ResultData.success(userVO);
    }

    private String generateUniqueName() {
        String name;
        String characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
        int length = 6; // 生成的随机字符串长度
        StringBuilder sb = new StringBuilder();
        Random random = new Random();
        do {
            sb.setLength(0); // 清空StringBuilder
            sb.append("用户");
            for (int i = 0; i < length; i++) {
                int index = random.nextInt(characters.length());
                sb.append(characters.charAt(index));
            }
            name = sb.toString();
        } while (userMapper.checkNameExists(name) > 0);
        return name;
    }
    @Override
    public ResultData<String> genRandom(SmsLogin smsLogin, String clientIp){
        //入参校验
        if (smsLogin.getPhoneNumber() == null || smsLogin.getPhoneNumber().trim().isEmpty()) {
            throw new IllegalArgumentException("手机号不能为空");
        }
        if (!isMobile(smsLogin.getPhoneNumber())) {
            throw new IllegalArgumentException("手机号码格式错误，请更换后重试");
        }
        //发送参数
        AliyunSms aliyunSms = this.aliyunSMS(smsLogin.getPhoneNumber());
        // 发送验证码
        return this.sendAliyunMsg(aliyunSms,clientIp);
    }


    private boolean isMobile(String phoneNumber) {
        if (phoneNumber == null || phoneNumber.trim().isEmpty()) {
            return false;
        }
        return phoneNumber.matches(MOBILE_PATTERN);
    }

    public ResultData sendAliyunMsg(AliyunSms aliyunSms, String clientIp){
        //检查同一IP10分钟内发送次数是否超限制
        String countKey = "ip_count:" + clientIp;
        String countStr = redisTemplate.opsForValue().get(countKey);
        int count = (countStr == null) ? 0 : Integer.parseInt(countStr); // 处理null值

        if (count >= 3) {
            return ResultData.fail(ReturnCode.RC1005.getCode(), ReturnCode.RC1005.getMessage());
        }

        // 增加计数并设置过期时间
        redisTemplate.opsForValue().increment(countKey, 1);
        redisTemplate.expire(countKey, 10, TimeUnit.MINUTES);
        // 使用工具类生成六位的数字验证码
        String  code = BaseUtil.getRandomCode(aliyunSms.getVerifySize());
        // 将redisTemplate模板对象的key的序列化方式修改为new StringRedisSerializer
        redisTemplate.setKeySerializer(new StringRedisSerializer());
        // 将PhoneNumber当做key，将code当做value存进redis中，时间为10分钟
        redisTemplate.opsForValue().set(aliyunSms.getPhoneNumber(), code, 10, TimeUnit.MINUTES);
        // 获取信息发送成功与否的标志
        boolean flag = this.send(aliyunSms,code);
        // 根据信息是否发送成功，返回不同的内容
        if (flag){
            return ResultData.success("验证码发送成功");
        } else {
            return ResultData.fail(ReturnCode.RC999.getCode(),"验证码发送失败");
        }
    }

    private AliyunSms aliyunSMS(String phoneNumber) {
        AliyunSms aliyun = new AliyunSms();
        // 签名
        aliyun.setSignName(AliyunConstant.ALIYUN_SMS_SIGNNAME);
        // 模板编码
        aliyun.setTemplateCode(AliyunConstant.ALIYUN_SMS_TEMPLATECODE);
        // 失效时间
        aliyun.setTimeout(AliyunConstant.ALIYUN_SMS_TIMEOUT);
        // 验证码长度
        aliyun.setVerifySize(AliyunConstant.ALIYUN_SMS_VERIFY_SIZE);
        // 手机号
        aliyun.setPhoneNumber(phoneNumber);
        return aliyun;
    }
    public boolean send(AliyunSms aliyunSms,String code) {
        // 连接阿里云
        DefaultProfile profile = DefaultProfile.getProfile("cn-hangzhou", accessKeyId, accessKeySecret);
        IAcsClient client = new DefaultAcsClient(profile);
        // 构建请求
        CommonRequest request = new CommonRequest();
        // 请求方式
        request.setSysMethod(MethodType.POST);
        // 官方需要的和短信请求相关的信息
        request.setSysDomain("dysmsapi.aliyuncs.com");
        request.setSysVersion("2017-05-25");
        request.setSysAction("SendSms");
        // 生成装有短信验证码的map
        Map<String,Object> messageMap = new HashMap<>();
        messageMap.put("code", code);
        // 填写请求参数
        request.putQueryParameter("PhoneNumbers", aliyunSms.getPhoneNumber());
        // 签名名称
        request.putQueryParameter("SignName", aliyunSms.getSignName());
        //模板CODE
        request.putQueryParameter("TemplateCode", aliyunSms.getTemplateCode());
        // 短信模板变量对应的实际值
        request.putQueryParameter("TemplateParam", JSONObject.toJSONString(messageMap));
        try {
            // 发送请求并接受返回值
            CommonResponse response = client.getCommonResponse(request);
            // 把json格式字符串变成Json对象
            JSONObject jsonObject = JSON.parseObject(response.getData());
            // 请求状态码，返回OK代表请求成功，来自官方文档
            String resCode = jsonObject.getString("Code");
            return "OK".equals(resCode);
        } catch (ServerException e) {
            e.printStackTrace();
        } catch (ClientException e) {
            e.printStackTrace();
        }
        return false;
    }
}



