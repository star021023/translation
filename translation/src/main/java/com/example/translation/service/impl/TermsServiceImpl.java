package com.example.translation.service.impl;

import com.example.translation.mapper.TermsMapper;
import com.example.translation.pojo.po.Terms;
import com.example.translation.service.TermsService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class TermsServiceImpl implements TermsService {
    @Autowired
    private TermsMapper termsMapper;
    @Override
    public List<Terms> selectAllTerms(){
        return termsMapper.selectAllTerms();
    }

    @Override
    public List<Terms> selectByKeywords(String keywords){
        return termsMapper.selectByKeywords(keywords);
    }

    @Override
    public int deleteById(int id){
        return termsMapper.deleteById(id);
    }

    @Override
    public int updateTerms(Terms terms){
        return termsMapper.updateTerms(terms);
    }

    @Override
    public int insertTerms(Terms terms){
        return termsMapper.insertTerms(terms);
    }
}
