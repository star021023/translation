package com.example.translation.service;

import com.example.translation.common.result.ResultData;
import com.example.translation.pojo.po.ParallelCorpus;
import com.example.translation.pojo.po.Terms;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;

public interface TermsService {
    List<Terms> selectAllTerms();

    List<Terms> selectByKeywords(String keywords);

    int deleteById(int id);

    int updateTerms(Terms terms);

    int insertTerms(Terms terms);

    List<ParallelCorpus> selectAllParallelCorpus();

    List<ParallelCorpus> searchParallelCorpus(String keywords);

    int deleteParallelCorpus(int id);

    int updateParallelCorpus(ParallelCorpus parallelCorpus);

    int insertParallelCorpus(ParallelCorpus parallelCorpus);


    ResultData importParallelCorpus(MultipartFile file);
}
