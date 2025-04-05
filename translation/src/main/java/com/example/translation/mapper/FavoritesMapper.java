package com.example.translation.mapper;
import com.example.translation.pojo.po.Favorites;
import com.example.translation.pojo.vo.FavoriteVO;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Options;
import java.util.List;
@Mapper
public interface FavoritesMapper {
    @Options(useGeneratedKeys = true, keyProperty = "id")
    void insertFavorites(Favorites favorites);
    int deleteFavoritesById(long id,long userId);
    int updateFavorites(Favorites favorites);
    Favorites selectFavoritesById(long id);
    List<FavoriteVO> selectAllFavorites(long userId);
    List<Favorites> selectFavoritesByUserIdAndText(Long userId, String text);
}
