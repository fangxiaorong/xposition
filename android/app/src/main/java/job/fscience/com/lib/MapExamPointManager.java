package job.fscience.com.lib;

import android.content.Context;
import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import com.amap.api.maps.AMap;
import com.amap.api.maps.model.BitmapDescriptorFactory;
import com.amap.api.maps.model.LatLng;
import com.amap.api.maps.model.Marker;
import com.amap.api.maps.model.MarkerOptions;
import job.fscience.com.xposition.R;

import java.util.ArrayList;
import java.util.List;

public class MapExamPointManager {
    private AMap map;
    private Context context;
    private int[] icons = new int[] {R.mipmap.c1, R.mipmap.c2, R.mipmap.c3, R.mipmap.c4, R.mipmap.c5, R.mipmap.c6,
            R.mipmap.c7, R.mipmap.c8, R.mipmap.c9, R.mipmap.c10, R.mipmap.c11, R.mipmap.c12, R.mipmap.c13, R.mipmap.c14,
            R.mipmap.c15, R.mipmap.c16, R.mipmap.c17, R.mipmap.c18, R.mipmap.c19, R.mipmap.c20, R.mipmap.c21,
            R.mipmap.c22, R.mipmap.c23, R.mipmap.c24, R.mipmap.c25, R.mipmap.c26};
    private List<Marker> points = new ArrayList<>();

    public MapExamPointManager(Context context, AMap map) {
        this.map = map;
        this.context = context;
    }

    public void showMarks(JSONArray marks) {
        hidden();
        int markSize = marks.size();
        int pointSize = points.size();

        int i = 0;
        int size = Math.min(markSize, pointSize);
        for (; i < size; i++) {
            JSONObject mark = marks.getJSONObject(i);
            points.get(i).setPosition(new LatLng(mark.getDouble("latitude"), mark.getDouble("longitude")));
            points.get(i).setVisible(true);
        }
        for (; i < markSize; i++) {
            JSONObject mark = marks.getJSONObject(i);
            MarkerOptions markerOption = new MarkerOptions();
            markerOption.icon(BitmapDescriptorFactory.fromResource(icons[Math.min(i, 25)]));
            markerOption.position(new LatLng(mark.getDouble("latitude"), mark.getDouble("longitude")));
            markerOption.setFlat(true);
            Marker marker = map.addMarker(markerOption);
            points.add(marker);
        }
    }

    public void hidden() {
        for (Marker point : points) {
            point.setVisible(false);
        }
    }
}
