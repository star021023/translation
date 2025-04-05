package com.example.translation.pojo.dto;


import lombok.Data;

@Data
public class AliyunSms {

    /**
     * 签名
     */
    private String signName;

    /**
     * 模板编码
     */
    private String templateCode;

    /**
     * 失效时间
     */
    private Integer timeout;

    /**
     * 验证码长度
     */
    private Integer verifySize;

    /**
     * 手机号码
     */
    private String phoneNumber;
}
