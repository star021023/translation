package com.example.translation.service;

import com.example.translation.common.result.ResultData;
import com.example.translation.pojo.po.SmsLogin;
import com.example.translation.pojo.vo.UserVO;

import java.util.Map;

public interface UserService {

    ResultData<String> registerUser(String username, String password);


    ResultData<UserVO>  login(String username, String password);


    ResultData<String> genRandom(SmsLogin smsLogin, String clientIp);
}
