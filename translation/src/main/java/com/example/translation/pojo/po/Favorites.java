package com.example.translation.pojo.po;

import lombok.Data;

import java.util.Date;
@Data
public class Favorites {
    private long id;
    private long userId;
    private String sourceLang;
    private String targetLang;
    private String sourceText;
    private String targetText;
    private String reflect;
    private String reflectText;
    private Date createTime;
    private Date updateTime;
}
