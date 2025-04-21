package com.example.translation.mapper;

import com.example.translation.pojo.po.ParallelCorpus;
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

    List<ParallelCorpus> selectAllParallelCorpus();
    List<ParallelCorpus> searchParallelCorpus(String keywords);
    int deleteParallelCorpus(int id);
    int updateParallelCorpus(ParallelCorpus parallelCorpus);
    int insertParallelCorpus(ParallelCorpus parallelCorpus);
    void batchInsertParallelCorpus(List<ParallelCorpus> parallelCorpusList);
}
