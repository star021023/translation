package com.example.translation.pojo.dto;

import lombok.Data;

@Data
public class ResetPasswordDTO {
    private String phoneNumber;
    private String verifyCode;
    private String newPassword;
}
