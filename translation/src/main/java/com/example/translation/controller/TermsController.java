package com.example.translation.controller;

import com.example.translation.pojo.po.Terms;
import com.example.translation.service.TermsService;
import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping(("/terms"))
public class TermsController {
    @Autowired
    public TermsService termsService;

    @GetMapping("/getAll")
    public PageInfo<Terms> getUserList(
            @RequestParam(defaultValue = "1") Integer pageNum,
            @RequestParam(defaultValue = "20") Integer pageSize) {
        // 使用PageHelper分页
        PageHelper.startPage(pageNum, pageSize);
        List<Terms> terms = termsService.selectAllTerms();
        return new PageInfo<>(terms);
    }

    @GetMapping("/search")
    public PageInfo<Terms> selectByKeywords(
            @RequestParam String keywords,
            @RequestParam(defaultValue = "1") Integer pageNum,
            @RequestParam(defaultValue = "20") Integer pageSize){
        PageHelper.startPage(pageNum, pageSize);
        List<Terms> terms = termsService.selectByKeywords(keywords);
        return new PageInfo<>(terms);
    }

    @DeleteMapping("/delete/{id}")
    public int deleteById(@PathVariable int id){
        return termsService.deleteById(id);
    }

    @PutMapping("/update")
    public int updateTerms(@RequestBody Terms terms){
        return termsService.updateTerms(terms);
    }
    @PostMapping("/insert")
    public int addTerms(@RequestBody Terms terms){
        return termsService.insertTerms(terms);
    }

}
