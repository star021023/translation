package com.example.translation.controller;

import com.example.translation.pojo.po.Favorites;
import com.example.translation.pojo.vo.FavoriteVO;
import com.example.translation.pojo.vo.HistoryVO;
import com.example.translation.service.FavoritesService;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/favorites")
public class FavoritesController {
    @Autowired
    private FavoritesService favoritesService;

    // 插入一条收藏记录
    @PostMapping("/add")
    public FavoriteVO insertFavorites(@RequestBody Favorites favorites) {
        Favorites favor= favoritesService.insertFavorites(favorites);
        FavoriteVO favoriteVO=new FavoriteVO();
        favoriteVO.setId(favor.getId());
        return favoriteVO;
    }

    // 根据 ID 删除一条收藏记录
    @DeleteMapping("/delete/{id}")
    public int deleteFavoritesById(@PathVariable Long id) {
        return favoritesService.deleteFavoritesById(id);
    }

    // 更新一条收藏记录
    @PutMapping
    public int updateFavorites(@RequestBody Favorites favorites){
        return favoritesService.updateFavorites(favorites);
    }
    @GetMapping("/{id}")
    public Favorites selectHistoryById(@PathVariable Long id) {
        return favoritesService.selectFavoritesById(id);
    }
    @GetMapping("/getAll")
    public List<FavoriteVO>  selectAllFavorites() {
        return favoritesService.selectAllFavorites();
    }
    @GetMapping("/search")
    public List<FavoriteVO>  selectAllHistories(@RequestParam String text) {
        return favoritesService.searchFavorites(text);
    }
}
