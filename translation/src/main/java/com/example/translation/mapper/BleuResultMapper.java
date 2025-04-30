package com.example.translation.mapper;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;

import java.util.List;

@Mapper
public interface BleuResultMapper {
    @Select("SELECT first_score FROM bleu_results WHERE type=0")
    List<Double> selectFirstScores0();

    @Select("SELECT improve_score FROM bleu_results WHERE type=0")
    List<Double> selectImproveScores0();
    @Select("SELECT first_score FROM bleu_results WHERE type=1")
    List<Double> selectFirstScores1();

    @Select("SELECT improve_score FROM bleu_results WHERE type=1")
    List<Double> selectImproveScores1();
}
