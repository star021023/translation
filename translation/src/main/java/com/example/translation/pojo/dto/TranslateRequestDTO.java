package com.example.translation.pojo.dto;

import lombok.Data;

@Data
public class TranslateRequestDTO {
   private String sourceLanguage;
   private String targetLanguage;
   private String sourceText;
   private boolean termbases;
}
