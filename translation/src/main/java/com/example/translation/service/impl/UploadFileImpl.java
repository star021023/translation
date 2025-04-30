package com.example.translation.service.impl;

import com.aliyun.oss.OSS;
import com.aliyun.oss.OSSClientBuilder;
import com.example.translation.common.Interceptor.UserContext;
import com.example.translation.common.result.ResultData;
import com.example.translation.common.result.ReturnCode;
import com.example.translation.common.util.ConstantPropertiesUtil;
import com.example.translation.common.util.JwtUtil;
import com.example.translation.mapper.AdminMapper;
import com.example.translation.mapper.UserMapper;
import com.example.translation.pojo.dto.DataChunk;
import com.example.translation.pojo.dto.ImgTranslDTO;
import com.example.translation.pojo.po.User;
import com.example.translation.pojo.vo.UserVO;
import com.example.translation.service.TranslateService;
import com.example.translation.service.UploadFile;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.codec.ServerSentEvent;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;
import reactor.core.publisher.Flux;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.List;
import java.util.UUID;

@Service
public class UploadFileImpl implements UploadFile {
    @Autowired
    private UserMapper userMapper;
    @Autowired
    private AdminMapper adminMapper;
    @Autowired
    private TranslateService translateService;

    @Value("${file.upload.img-dir}")
    private String imgDir;

    @Value("${file.upload.allowed-types}")
    private String allowedTypesStr;
    private List<String> getAllowedTypes() {
        return Arrays.asList(allowedTypesStr.split(","));
    }
    @Override
    public ResultData<UserVO> uploadFileAvatar(MultipartFile multipartFile) {
        Long userId = UserContext.getUserId();
        String endpoint = ConstantPropertiesUtil.END_POINT;
        String accessKeyId = ConstantPropertiesUtil.KEY_ID;
        String accessKeySecret = ConstantPropertiesUtil.KEY_SECRET;
        // 填写Bucket名称
        String bucketName = ConstantPropertiesUtil.BUCKET_NAME;
        // 创建OSSClient实例
        OSS ossClient = new OSSClientBuilder().build(endpoint, accessKeyId, accessKeySecret);
        try {
            InputStream inputStream = multipartFile.getInputStream();
            String originalFilename = multipartFile.getOriginalFilename();
            String fileExtension = originalFilename.substring(originalFilename.lastIndexOf("."));
            // 使用userId作为文件名
            String filename = userId + fileExtension;
            //调用oss方法实现上传
            ossClient.putObject(bucketName, filename, inputStream);
            String url = "https://".concat(bucketName).concat(".").concat(endpoint).concat("/").concat(filename);
            userMapper.updateAvatar(userId,url);
            User user=userMapper.findUserById(userId);
            UserVO userVO = new UserVO();
            String newToken = JwtUtil.generateToken(user.getId(), user.getName());
            userVO.setToken(newToken);
            userVO.setName(user.getName());
            userVO.setPhoneNumber(user.getPhone());
            userVO.setAvatar(user.getAvatar());
            return ResultData.success(userVO);
        }catch (Exception e){
            e.printStackTrace();
            return null;
        }finally {
            if (ossClient != null) {
                ossClient.shutdown();
            }
        }
    }

    @Override
    public ResultData<UserVO> uploadAdminAvatar(MultipartFile multipartFile) {
        Long userId = UserContext.getUserId();
        String endpoint = ConstantPropertiesUtil.END_POINT;
        String accessKeyId = ConstantPropertiesUtil.KEY_ID;
        String accessKeySecret = ConstantPropertiesUtil.KEY_SECRET;
        // 填写Bucket名称
        String bucketName = ConstantPropertiesUtil.BUCKET_NAME;
        // 创建OSSClient实例
        OSS ossClient = new OSSClientBuilder().build(endpoint, accessKeyId, accessKeySecret);
        try {
            InputStream inputStream = multipartFile.getInputStream();
            String originalFilename = multipartFile.getOriginalFilename();
            String fileExtension = originalFilename.substring(originalFilename.lastIndexOf("."));
            // 使用userId作为文件名
            String filename = userId + fileExtension;
            //调用oss方法实现上传
            ossClient.putObject(bucketName, filename, inputStream);
            String url = "https://".concat(bucketName).concat(".").concat(endpoint).concat("/").concat(filename);
            adminMapper.updateAvatar(userId,url);
            User user=adminMapper.findAdminById(userId);
            UserVO userVO = new UserVO();
            String newToken = JwtUtil.generateToken(user.getId(), user.getName());
            userVO.setToken(newToken);
            userVO.setName(user.getName());
            userVO.setPhoneNumber(user.getPhone());
            userVO.setAvatar(user.getAvatar());
            userVO.setAdmin(true);
            return ResultData.success(userVO);
        }catch (Exception e){
            e.printStackTrace();
            return null;
        }finally {
            if (ossClient != null) {
                ossClient.shutdown();
            }
        }
    }
    @Override
    public Flux<ServerSentEvent<DataChunk>> imgUpload(String sourceLanguage, String targetLanguage, MultipartFile multipartFile) {
        try {
            // 校验文件类型
            String contentType = multipartFile.getContentType();
            if (contentType == null || !getAllowedTypes().contains(contentType)) {
                return Flux.just(ServerSentEvent.<DataChunk>builder()
                        .event("error")
                        .data(new DataChunk("error", ReturnCode.RC999.getCode(), "仅支持JPEG/PNG/GIF图片"))
                        .build());
            }

            // 确保目录存在
            File uploadDir = new File(imgDir);
            if (!uploadDir.exists()) {
                uploadDir.mkdirs();
            }

            // 生成唯一文件名
            String originalFilename = multipartFile.getOriginalFilename();
            String fileExtension = originalFilename.substring(originalFilename.lastIndexOf("."));
            String newFilename = UUID.randomUUID() + fileExtension;

            // 保存文件
            Path filePath = Paths.get(imgDir, newFilename);
            multipartFile.transferTo(filePath);
            String imgPath = imgDir+ "/" + newFilename;
            ImgTranslDTO dto = new ImgTranslDTO();
            dto.setSourceLanguage(sourceLanguage);
            dto.setTargetLanguage(targetLanguage);
            dto.setImgPath(imgPath);
            return translateService.imgTranslate(dto);

        } catch (IOException e) {
            return Flux.just(ServerSentEvent.<DataChunk>builder()
                    .event("error")
                    .data(new DataChunk("error", ReturnCode.RC999.getCode(), "图片上传失败"))
                    .build());
        }
    }

    @Override
    public ResultData<String> uploadWord(String sourceLanguage, String targetLanguage, MultipartFile multipartFile){
        try {
            String originalFilename = multipartFile.getOriginalFilename();
            String fileExtension = originalFilename.substring(originalFilename.lastIndexOf(".")).toLowerCase();
            if (!Arrays.asList(".doc", ".docx").contains(fileExtension)) {
                return ResultData.fail(ReturnCode.RC999.getCode(), "仅支持DOC/DOCX文件");
            }
            File uploadDir = new File(imgDir);
            if (!uploadDir.exists()) {
                uploadDir.mkdirs();
            }
            String newFilename = UUID.randomUUID() + fileExtension;
            Path filePath = Paths.get(imgDir, newFilename);
            multipartFile.transferTo(filePath);
            String docPath = imgDir+ "/" + newFilename;
            ImgTranslDTO dto = new ImgTranslDTO();
            dto.setSourceLanguage(sourceLanguage);
            dto.setTargetLanguage(targetLanguage);
            dto.setImgPath(docPath);
            return translateService.docTranslate(dto);
        } catch (Exception  e) {
            return ResultData.fail(ReturnCode.RC999.getCode(), "文档处理失败: " + e.getMessage());
        }
    }
}
