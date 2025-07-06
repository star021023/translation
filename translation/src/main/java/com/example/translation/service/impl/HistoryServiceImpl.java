package com.example.translation.service.impl;

import com.example.translation.common.Interceptor.UserContext;
import com.example.translation.mapper.DocHistoryMapper;
import com.example.translation.mapper.HistoryMapper;
import com.example.translation.mapper.ImgHistoryMapper;
import com.example.translation.pojo.po.DocHistory;
import com.example.translation.pojo.po.History;
import com.example.translation.pojo.po.ImgHistory;
import com.example.translation.pojo.vo.HistoryVO;
import com.example.translation.pojo.vo.ImgHistoryVO;
import com.example.translation.service.HistoryService;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class HistoryServiceImpl implements HistoryService {
    @Autowired
    private HistoryMapper historyMapper;
    @Autowired
    private ImgHistoryMapper imgHistoryMapper;
    @Autowired
    private DocHistoryMapper docHistoryMapper;
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
    @Override
    public List<ImgHistoryVO> selectAllImgHistory(){
        Long userId = UserContext.getUserId();
        return imgHistoryMapper.selectImgHistory(userId);
    }
    @Override
    public int deleteImgHistory(Long id){
        Long userId = UserContext.getUserId();
        return imgHistoryMapper.deleteImgHistory(id,userId);
    }
    @Override
    public int insertImgHistory(ImgHistory imgHistory){
        return imgHistoryMapper.insertImgHistory(imgHistory);
    }
    @Override
    public List<ImgHistoryVO> searchImgHistories(String text){
        Long userId = UserContext.getUserId();
        return imgHistoryMapper.searchImgHistories(userId,text);
    }

    @Override
    public List<DocHistory> selectDocHistories(){
        Long userId = UserContext.getUserId();
        return docHistoryMapper.selectDocHistory(userId);
    }

    @Override
    public int insertDocHistory(DocHistory docHistory){
        return docHistoryMapper.insert(docHistory);
    }
    @Override
    public int deleteDocHistory(Long id){
        Long userId = UserContext.getUserId();
        return docHistoryMapper.deleteById(id,userId);
    }
}
