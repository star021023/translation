package com.example.translation.service;

import com.example.translation.pojo.po.Terms;

import java.util.List;

public interface TermsService {
    List<Terms> selectAllTerms();

    List<Terms> selectByKeywords(String keywords);

    int deleteById(int id);

    int updateTerms(Terms terms);

    int insertTerms(Terms terms);
}
