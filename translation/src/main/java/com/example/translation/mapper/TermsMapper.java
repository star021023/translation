package com.example.translation.mapper;

import com.example.translation.pojo.po.Terms;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;
@Mapper
public interface TermsMapper {
    List<Terms> selectByKeywords(String keywords);
    List<Terms> selectAllTerms();
    int deleteById(int id);
    int insertTerms(Terms terms);
    int updateTerms(Terms terms);
}
