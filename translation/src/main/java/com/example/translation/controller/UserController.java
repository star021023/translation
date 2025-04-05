package com.example.translation.controller;

import com.aliyuncs.CommonResponse;
import com.example.translation.common.result.ResultData;
import com.example.translation.common.util.IpUtil;
import com.example.translation.pojo.dto.AccountDTO;
import com.example.translation.pojo.po.SmsLogin;
import com.example.translation.pojo.vo.UserVO;
import com.example.translation.service.UserService;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;


@RestController
public class UserController {
    @Autowired
    private UserService userService;
    @PostMapping("/register")
    public ResultData<String> registerUser(@RequestBody AccountDTO accountDTO){
        return userService.registerUser(accountDTO.getUsername(), accountDTO.getPassword());
    }
    @PostMapping("/login")
    public ResultData<UserVO> login(@RequestBody AccountDTO accountDTO){
        return userService.login(accountDTO.getUsername(), accountDTO.getPassword());
    }

    @PostMapping( "/genRandom")
    public ResultData<String> genRandom(@RequestBody SmsLogin smsLogin, HttpServletRequest request) throws Exception {
        String clientIp = IpUtil.getClientIP(request);
        return userService.genRandom(smsLogin, clientIp);
    }

}
