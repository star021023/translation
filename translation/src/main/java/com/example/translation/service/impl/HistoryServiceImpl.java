package com.example.translation.service.impl;

import com.example.translation.mapper.HistoryMapper;
import com.example.translation.pojo.po.History;
import com.example.translation.pojo.vo.HistoryVO;
import com.example.translation.service.HistoryService;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class HistoryServiceImpl implements HistoryService {
    @Autowired
    private HistoryMapper historyMapper;
    @Override
    public int insertHistory(History history) {
        return historyMapper.insertHistory(history);
    }

    @Override
    public int deleteHistoryById(Long id, HttpServletRequest request) {
        Long userId = (Long) request.getAttribute("userId");
        return historyMapper.deleteHistoryById(id,userId);
    }

    @Override
    public int updateHistory(History history) {
        return historyMapper.updateHistory(history);
    }

    @Override
    public List<HistoryVO> searchHistories(String text, HttpServletRequest request){
        Long userId = (Long) request.getAttribute("userId");
        return historyMapper.searchHistories(userId,text);
    }
    @Override
    public List<HistoryVO> selectAllHistories(HttpServletRequest request) {
        Long userId = (Long) request.getAttribute("userId");
        return historyMapper.selectAllHistories(userId);
    }

}
