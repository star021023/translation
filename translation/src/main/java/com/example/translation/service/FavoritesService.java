package com.example.translation.service;

import com.example.translation.pojo.po.Favorites;
import com.example.translation.pojo.vo.FavoriteVO;

import java.util.List;

public interface FavoritesService {


    Favorites insertFavorites(Favorites favorites);

    int deleteFavoritesById(Long id);

    int updateFavorites(Favorites favorites);

    Favorites selectFavoritesById(Long id);


    List<FavoriteVO> selectAllFavorites();


    List<FavoriteVO> searchFavorites(String text);
}
