package com.example.translation.controller;

import com.example.translation.common.result.ResultData;
import com.example.translation.common.result.ReturnCode;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;


@RestController
@RequestMapping("/test")
public class TestController {

    @GetMapping("/wrong")
    public int error(){
            int i = 9/0;
            return i;
    }
    @GetMapping("error1")
    public void empty(){
        throw  new RuntimeException("账号密码不正确");
    }
}
