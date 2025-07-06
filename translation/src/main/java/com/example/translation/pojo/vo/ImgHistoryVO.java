package com.example.translation.pojo.vo;

import lombok.Data;

import java.util.Date;
@Data
public class ImgHistoryVO {
    private long id;
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
