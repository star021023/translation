package com.example.translation.pojo.dto;

import lombok.Data;

@Data
public class RegisterDTO {
    private String username;
    private String password;
    private String phoneNumber;
    private String verifyCode;
}
