package com.example.translation.pojo.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import lombok.Data;

@Data
@JsonIgnoreProperties(ignoreUnknown = true)
public class DataChunk {
    private String stage;
    private String chunk;
    private Integer progress;

    public DataChunk(String error, int code, String s) {
    }
}
