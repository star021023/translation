package com.example.translation.pojo.po;

import lombok.Data;

import java.util.Date;

@Data
public class User {
    private long id;
    private String username;
    private String password;
    private String name;
    private String avatar;
    private String phone;
    private Date createTime;
    private Date updateTime;
}
