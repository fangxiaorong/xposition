package job.fscience.com.lib;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Color;
import android.text.TextPaint;
import com.amap.api.maps.AMap;
import com.amap.api.maps.model.BitmapDescriptorFactory;
import com.amap.api.maps.model.LatLng;
import com.amap.api.maps.model.Marker;
import com.amap.api.maps.model.MarkerOptions;
import job.fscience.com.xposition.R;

import java.util.HashMap;
import java.util.Map;

public class MapMarkManager {
    public static final int USER_STATE_ONLINE = 1;
    public static final int USER_STATE_OFFLINE = 2;
    public static final int USER_STATE_DEADLINE = 3;

    private AMap map;
    private Context context;

    Map<String, Bitmap> iconMap = new HashMap<>();
    Map<String, Bitmap> usersBitmap = new HashMap<>();

    public MapMarkManager(Context context, AMap map) {
        this.map = map;
        this.context = context;

        loadSpirits();
    }

    private void loadSpirits() {
        Bitmap bitmap = BitmapFactory.decodeResource(context.getResources(), R.mipmap.sprite);

        double xScale = bitmap.getWidth() / 460.0;
        double yScale = bitmap.getHeight() / 1964.0;
        int size = (int)(55 * xScale);
        iconMap.put("position", Bitmap.createBitmap(bitmap, 0, (int)(yScale * 1375.0), size, size));
        iconMap.put("person_online", Bitmap.createBitmap(bitmap, (int)(300 * xScale), (int)(yScale * 1480), (int)(120 * xScale), size));
        iconMap.put("person_offline", Bitmap.createBitmap(bitmap, (int)(180 * xScale), (int)(yScale * 1480), (int)(120 * xScale), size));
        iconMap.put("dest", Bitmap.createBitmap(bitmap, 0, (int)(yScale * 650), size, size));
        iconMap.put("dest1", Bitmap.createBitmap(bitmap, (int)(220 * xScale), (int)(yScale * 440), size, size));
        iconMap.put("delete", Bitmap.createBitmap(bitmap, (int)(220 * xScale), (int)(yScale * 590), size, size));

        bitmap.recycle();
    }

    private Bitmap getUserBitmap(String userName, boolean online) {
        Bitmap userBitmap = usersBitmap.get(userName + (online ? "O" : "F"));
        if (userBitmap == null) {
            Bitmap bitmap = online ? iconMap.get("person_online") : iconMap.get("person_offline");
            userBitmap = Bitmap.createBitmap(bitmap, 0, 0, bitmap.getWidth(), bitmap.getHeight());
            Canvas canvas = new Canvas(bitmap);
            TextPaint textPaint = new TextPaint();
            textPaint.setAntiAlias(true);
            textPaint.setTextSize(22f);
            textPaint.setColor(Color.rgb(25, 25, 25));
            canvas.drawText(userName, 17, 35, textPaint);
        }
        return userBitmap;
    }

    Map<Integer, Marker> userMap = new HashMap<>();
    public void updateUser(Integer userId, String userName, Double latitude, Double longitude, Integer state) {
        Marker marker = userMap.get(userId);
        if (marker != null) {
            if (!state.equals(marker.getObject())) {
                if (state == USER_STATE_DEADLINE) {
                    marker.setVisible(false);
                } else {
                    marker.setVisible(true);
                    marker.setIcon(BitmapDescriptorFactory.fromBitmap(getUserBitmap(userName, state == USER_STATE_ONLINE)));
                }
            }
            if (state != USER_STATE_DEADLINE) {
                marker.setPosition(new LatLng(latitude, longitude));
            }
        } else {
            MarkerOptions markerOption = new MarkerOptions();
            markerOption.position(new LatLng(latitude == null ? 0 : latitude, longitude == null ? 0 : longitude));
            markerOption.icon(BitmapDescriptorFactory.fromBitmap(getUserBitmap(userName, state == USER_STATE_ONLINE)));
            // 将Marker设置为贴地显示，可以双指下拉地图查看效果
            markerOption.setFlat(true);//设置marker平贴地图效果
            marker = map.addMarker(markerOption);
            userMap.put(userId, marker);
            if (state == USER_STATE_DEADLINE) {
                marker.setVisible(false);
            }
        }
        marker.setObject(state);
    }
}
