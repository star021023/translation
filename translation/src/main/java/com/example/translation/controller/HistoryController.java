package com.example.translation.controller;

import com.example.translation.pojo.po.Favorites;
import com.example.translation.pojo.po.History;
import com.example.translation.pojo.vo.HistoryVO;
import com.example.translation.service.HistoryService;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/history")
public class HistoryController {
    @Autowired
    private HistoryService historyService;

    // 插入一条历史记录
    @PostMapping
    public int insertHistory(@RequestBody History history) {
        return historyService.insertHistory(history);
    }

    // 根据 ID 删除一条历史记录
    @DeleteMapping("/delete/{id}")
    public int deleteHistoryById(@PathVariable Long id, HttpServletRequest request) {
        return historyService.deleteHistoryById(id,request);
    }

    // 更新一条历史记录
    @PutMapping
    public int updateHistory(@RequestBody History history) {
        return historyService.updateHistory(history);
    }
    @GetMapping("/search")
    public List<HistoryVO>  searchHistories(@RequestParam String text,HttpServletRequest request) {
        return historyService.searchHistories(text,request);
    }
    @GetMapping("/getAll")
    public List<HistoryVO>  selectAllHistories(HttpServletRequest request) {
        return historyService.selectAllHistories(request);
    }
}
