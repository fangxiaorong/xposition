package job.fscience.com.lib;

import android.app.Activity;
import android.content.Context;
import android.graphics.Color;
import android.support.v4.app.ActivityCompat;
import android.widget.Toast;
import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import com.amap.api.maps.MapView;
import com.amap.api.maps.model.LatLng;
import com.amap.api.maps.model.Polyline;
import com.amap.api.maps.model.PolylineOptions;
import job.fscience.com.net.ServerRequest;
import job.fscience.com.xposition.MainActivity;
import job.fscience.com.xposition.XApplication;
import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.Response;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class MapLineManager {
    private Activity activity;
    private MapView mapView;
    private Polyline polyline = null;

    public MapLineManager(Activity activity, MapView mapView) {
        this.activity = activity;
        this.mapView = mapView;
    }

    private void removePolyline() {
        if (polyline != null) {
            polyline.remove();
            polyline = null;
        }
    }

    public void updateLine(JSONArray points) {
        removePolyline();

        List<LatLng> latLngs = new ArrayList<>();
        for (int idx = 0; idx < points.size(); idx ++) {
            JSONObject point = points.getJSONObject(idx);
            latLngs.add(new LatLng(point.getDouble("latitude"), point.getDouble("longitude")));
        }
        polyline = mapView.getMap().addPolyline(new PolylineOptions().
                addAll(latLngs).width(10).color(Color.argb(255, 1, 1, 1)));
    }

    public void showUserTrack(Integer userId) {
        //
    }

//    private void requireUserTrack(Integer userId, final boolean notify) {
//        XApplication.getServerInstance().managerGetUserTrack(userId, new Callback() {
//            @Override
//            public void onFailure(Call call, IOException e) {
//                if (notify) {
//                    showTextOnUIThread("网络问题");
//                }
//            }
//
//            @Override
//            public void onResponse(Call call, Response response) throws IOException {
//                final JSONObject object = ServerRequest.parseJSON(response);
//                if (object == null) {
//                    if (notify) {
//                    showTextOnUIThread("服务器问题");
//                    }
//                } else if (object.getInteger("state") == 1) {
//                    activity.runOnUiThread(new Runnable() {
//                        @Override
//                        public void run() {
//                            updateLine(object.getJSONArray("points"));
////                            try {
////                                JSONArray points = object.getJSONArray("points");
////                                List<LatLng> latLngs = new ArrayList<>();
////                                for (int idx = 0; idx < points.size(); idx ++) {
////                                    JSONObject point = points.getJSONObject(idx);
////                                    latLngs.add(new LatLng(point.getDouble("latitude"), point.getDouble("longitude")));
////                                }
////                                polyline = mapView.getMap().addPolyline(new PolylineOptions().
////                                        addAll(latLngs).width(10).color(Color.argb(255, 1, 1, 1)));
////                            } catch (Exception e) {}
//                        }
//                    });
//                } else {
//                    if (notify) {
//                        showTextOnUIThread(object.getString("message"));
//                    }
//                }
//            }
//        });
//    }

    private void showTextOnUIThread(final String message) {
        activity.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                Toast.makeText(activity, message, Toast.LENGTH_LONG).show();
            }
        });
    }
}
