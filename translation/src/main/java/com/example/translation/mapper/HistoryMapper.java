package com.example.translation.mapper;

import com.example.translation.pojo.po.History;
import com.example.translation.pojo.vo.HistoryVO;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;
@Mapper
public interface HistoryMapper {
    int insertHistory(History history);
    int deleteHistoryById(long id,long userId);
    int updateHistory(History history);
    List<HistoryVO> selectAllHistories(long userId);
    List<HistoryVO> searchHistories( Long userId,String text);
}
