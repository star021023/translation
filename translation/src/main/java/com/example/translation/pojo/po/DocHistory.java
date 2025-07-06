package com.example.translation.pojo.po;

import lombok.Data;

import java.util.Date;

@Data
public class DocHistory {
    private long id;
    private long userId;
    private String savePath;
    private String fileName;
    private Date createTime;
    private Date updateTime;
}
