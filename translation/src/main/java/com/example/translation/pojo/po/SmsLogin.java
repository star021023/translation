package com.example.translation.pojo.po;

import lombok.Data;

@Data
public class SmsLogin {
    private String Id;
    /**
     * 手机号码
     */
    private String phoneNumber;

    /**
     * 验证码
     */
    private String verifyCode;

    /**
     * 登录时间
     */
    private String creationTime;
}
