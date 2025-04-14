package com.example.translation.pojo.dto;

import lombok.Data;

@Data
public class ImgTranslDTO {
    private String sourceLanguage;
    private String targetLanguage;
    private String imgPath;
}
