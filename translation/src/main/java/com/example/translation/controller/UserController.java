package com.example.translation.controller;

import com.example.translation.common.result.ResultData;
import com.example.translation.common.util.IpUtil;
import com.example.translation.pojo.dto.AccountDTO;
import com.example.translation.pojo.dto.RegisterDTO;
import com.example.translation.pojo.dto.ResetPasswordDTO;
import com.example.translation.pojo.po.SmsLogin;
import com.example.translation.pojo.vo.UserVO;
import com.example.translation.service.UserService;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;


@RestController
public class UserController {
    @Autowired
    private UserService userService;
    @PostMapping("/register")
    public ResultData<String> registerUser(@RequestBody RegisterDTO registerDTO){
        return userService.registerUser(registerDTO);
    }
    @PostMapping("/login")
    public ResultData<UserVO> login(@RequestBody AccountDTO accountDTO){
        return userService.login(accountDTO.getUsername(), accountDTO.getPassword());
    }
    @PostMapping("/admin/login")
    public ResultData<UserVO> adminLogin(@RequestBody AccountDTO accountDTO){
        return userService.adminLogin(accountDTO.getUsername(), accountDTO.getPassword());
    }

    @PostMapping( "/genRandom")
    public ResultData<String> genRandom(@RequestBody SmsLogin smsLogin, HttpServletRequest request) throws Exception {
        String clientIp = IpUtil.getClientIP(request);
        return userService.genRandom(smsLogin, clientIp);
    }
    @PostMapping("/phoneLogin")
    public ResultData<UserVO> phoneLogin(@RequestBody SmsLogin smsLogin){
        return userService.phoneLogin(smsLogin.getPhoneNumber(),smsLogin.getVerifyCode());
    }
    @PutMapping("/updateName")
    public ResultData<UserVO> updateName(@RequestBody Map<String, String> request){
        return userService.updateName(request.get("name"));
    }
    @PutMapping("/admin/updateName")
    public ResultData<UserVO> updateAdminName(@RequestBody Map<String, String> request){
        return userService.updateAdminName(request.get("name"));
    }
    @PutMapping("/resetPassword")
    public ResultData<String> resetPasswordBySms(@RequestBody ResetPasswordDTO resetPasswordDTO) {
        return userService.resetPasswordBySms(
                resetPasswordDTO.getPhoneNumber(),
                resetPasswordDTO.getVerifyCode(),
                resetPasswordDTO.getNewPassword()
        );
    }

}
