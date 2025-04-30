package com.example.translation.service;

import com.example.translation.common.result.ResultData;
import com.example.translation.pojo.dto.RegisterDTO;
import com.example.translation.pojo.po.SmsLogin;
import com.example.translation.pojo.vo.UserVO;

import java.util.Map;

public interface UserService {



    ResultData<String> registerUser(RegisterDTO registerDTO);

    ResultData<UserVO>  login(String username, String password);


    ResultData<UserVO>  adminLogin(String username, String password);

    ResultData<UserVO>  phoneLogin(String phoneNumber, String verifyCode);

    ResultData<String> genRandom(SmsLogin smsLogin, String clientIp);

    ResultData<UserVO> updateName(String newName);

    ResultData<UserVO> updateAdminName(String newName);

    ResultData<String> resetPasswordBySms(String phoneNumber, String verifyCode, String newPassword);
}
