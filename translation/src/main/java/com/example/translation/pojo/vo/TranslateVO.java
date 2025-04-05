package com.example.translation.pojo.vo;

import lombok.Data;

import java.util.Date;
@Data
public class TranslateVO {
    private String sourceLang;
    private String targetLang;
    private String sourceText;
    private String targetText;
    private Date updateTime;
}
