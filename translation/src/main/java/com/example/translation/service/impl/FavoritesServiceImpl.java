package com.example.translation.service.impl;

import com.example.translation.common.Interceptor.UserContext;
import com.example.translation.mapper.FavoritesMapper;
import com.example.translation.pojo.po.Favorites;
import com.example.translation.pojo.vo.FavoriteVO;
import com.example.translation.service.FavoritesService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class FavoritesServiceImpl implements FavoritesService {
    @Autowired
    private FavoritesMapper favoritesMapper;

    @Override
    public Favorites insertFavorites(Favorites favorites) {
        Long userId = UserContext.getUserId();
        favorites.setUserId(userId);
        favoritesMapper.insertFavorites(favorites);
        System.out.println(favorites.getId());
        return favorites;
    }

    @Override
    public int deleteFavoritesById(Long id) {
        Long userId = UserContext.getUserId();
        return favoritesMapper.deleteFavoritesById(id,userId);
    }

    @Override
    public int updateFavorites(Favorites favorites) {
        return favoritesMapper.updateFavorites(favorites);
    }

    @Override
    public Favorites selectFavoritesById(Long id) {
        return favoritesMapper.selectFavoritesById(id);
    }

    @Override
    public List<FavoriteVO> selectAllFavorites() {
        Long userId = UserContext.getUserId();
        return favoritesMapper.selectAllFavorites(userId);
    }

    @Override
    public List<FavoriteVO> searchFavorites(String text) {
        Long userId = UserContext.getUserId();
        return favoritesMapper.selectFavoritesByUserIdAndText(userId, text);
    }
}
