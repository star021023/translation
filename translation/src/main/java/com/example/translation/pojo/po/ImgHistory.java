package com.example.translation.pojo.po;

import lombok.Data;

import java.util.Date;
@Data
public class ImgHistory {
    private long id;
    private long userId;
    private String sourceLang;
    private String targetLang;
    private String sourceText;
    private String targetText;
    private String reflect;
    private String reflectText;
    private String imgPath;
    private Date createTime;
    private Date updateTime;
}
