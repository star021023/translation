package com.example.translation.pojo.vo;

import lombok.Data;

import java.util.Date;

@Data
public class FavoriteVO {
    private Long id;
    private String sourceLang;
    private String targetLang;
    private String sourceText;
    private String targetText;
    private String reflect;
    private String reflectText;
    private Date createTime;
    private Date updateTime;
}
