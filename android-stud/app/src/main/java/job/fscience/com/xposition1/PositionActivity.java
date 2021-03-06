package job.fscience.com.xposition1;

import android.Manifest;
import android.app.AlarmManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.drawable.Drawable;
import android.location.LocationManager;
import android.os.Bundle;
import android.provider.Settings;
import android.support.v4.app.ActivityCompat;
import android.support.v4.content.ContextCompat;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.widget.TextView;
import android.widget.Toast;
import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import com.amap.api.maps.AMap;
import com.amap.api.maps.CameraUpdate;
import com.amap.api.maps.CameraUpdateFactory;
import com.amap.api.maps.MapView;
import com.amap.api.maps.model.*;
import job.fscience.com.lib.LocationForegoundService;
import job.fscience.com.server.PositionService;
import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.Response;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

public class PositionActivity extends AppCompatActivity {
    private static final int LOCATION_CODE = 1;

    private AMap mMap;
    private LatLng mLatLng;
    Intent serviceIntent = null;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_position);

        serviceIntent = new Intent();
        serviceIntent.setClass(this, LocationForegoundService.class);

        MapView mapView = (MapView) findViewById(R.id.map);
        mapView.onCreate(savedInstanceState);// 此方法必须重写
        mMap = mapView.getMap();
        mMap.setTrafficEnabled(false);// 显示实时交通状况
        //地图模式可选类型：MAP_TYPE_NORMAL,MAP_TYPE_SATELLITE,MAP_TYPE_NIGHT
        mMap.setMapType(AMap.MAP_TYPE_NORMAL);


        initIcons();
        // 格式设置
        TextView headTextView = (TextView)findViewById(R.id.head);
        Drawable headDrawable = getResources().getDrawable(R.mipmap.ic_launcher);
        headDrawable.setBounds(0, 0, 60, 60);
        headTextView.setCompoundDrawables(headDrawable, null, null, null);
        headTextView.setText(LoginActivity.userInfo.getString("username"));

        findViewById(R.id.upload).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                //上报位置
                if (mLatLng != null) {
                    XApplication.getServerInstance().userUploadPosition(LoginActivity.userInfo.getInteger("id"),
                            mLatLng.latitude, mLatLng.longitude, 1, new Callback() {
                        @Override
                        public void onFailure(Call call, IOException e) {
                            showTextOnUIThread("网络问题");
                        }

                        @Override
                        public void onResponse(Call call, Response response) throws IOException {
                            if (response.isSuccessful()) {
                                JSONObject data = JSONObject.parseObject(response.body().string());
                                if (data.getInteger("state") == 1) {
                                    showTextOnUIThread("上报成功");
                                } else {
                                    showTextOnUIThread(data.getString("message"));
                                }
                            } else {
                                showTextOnUIThread("服务器问题");
                            }
                        }
                    });
                } else {
                    showTextOnUIThread("正在定位...");
                }
            }
        });

        findViewById(R.id.warring).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if (mLatLng != null) {
                    XApplication.getServerInstance().userUploadWarring(LoginActivity.userInfo.getInteger("id"), mLatLng.latitude, mLatLng.longitude, new Callback() {
                        @Override
                        public void onFailure(Call call, IOException e) {
                            showTextOnUIThread("网路问题");
                        }

                        @Override
                        public void onResponse(Call call, Response response) throws IOException {
                            if (response.isSuccessful()) {
                                JSONObject data = JSONObject.parseObject(response.body().string());
                                if (data.getInteger("state") == 1) {
                                    showTextOnUIThread("报警成功");
                                } else {
                                    showTextOnUIThread(data.getString("message"));
                                }
                            } else {
                                showTextOnUIThread("服务器问题");
                            }
                        }
                    });
                }
            }
        });

        requestLocationPrivage();
    }

    private void startAlarm() {
        Intent intent = new Intent(this, PositionService.class);
        PendingIntent pendingIntent = PendingIntent.getService(this, 0, intent, 0);

        AlarmManager manager = (AlarmManager)getSystemService(Context.ALARM_SERVICE);
        manager.cancel(pendingIntent);
        manager.setRepeating(AlarmManager.RTC_WAKEUP, System.currentTimeMillis(), 3000, pendingIntent);
//        manager.setRepeating(AlarmManager.ELAPSED_REALTIME, System.currentTimeMillis(), 3000, pendingIntent);

//        AlarmManager alarmManager = (AlarmManager)getSystemService(Context.ALARM_SERVICE);
//        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
//            alarmManager.setExactAndAllowWhileIdle(AlarmManager.ELAPSED_REALTIME_WAKEUP, SystemClock.elapsedRealtime(), pendingIntent);
//        } else if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.KITKAT) {
//            alarmManager.setExact(AlarmManager.ELAPSED_REALTIME_WAKEUP, SystemClock.elapsedRealtime(), pendingIntent);
//        } else {
//            alarmManager.setRepeating(AlarmManager.ELAPSED_REALTIME_WAKEUP, SystemClock.elapsedRealtime(), 3000, pendingIntent);
//        }
    }

    private void stopAlarm() {
        Intent intent = new Intent(this, PositionService.class);
        PendingIntent pendingIntent = PendingIntent.getService(this, 0, intent, 0);

        AlarmManager manager = (AlarmManager)getSystemService(Context.ALARM_SERVICE);
        manager.cancel(pendingIntent);
    }

    BroadcastReceiver mBroadcastReceiver = null;
    @Override
    protected void onPause() {
        super.onPause();

        if (mBroadcastReceiver != null) {
            unregisterReceiver(mBroadcastReceiver);
            mBroadcastReceiver = null;
        }
        if (null != serviceIntent) {
            startService(serviceIntent);
        }
    }

    Marker positionMarker = null;
    boolean is_first_show = true;
    @Override
    protected void onResume() {
        super.onResume();

        is_first_show = true;
        if (mBroadcastReceiver == null) {
            mBroadcastReceiver = new BroadcastReceiver() {
                @Override
                public void onReceive(Context context, Intent intent) {
                    if (intent.getAction().equals(PositionService.ACTION_LOCATION)) {
                        if (intent.getIntExtra("state", -1) == 0) {
                            mLatLng = new LatLng(intent.getDoubleExtra("latitude", 0), intent.getDoubleExtra("longitude", 0));
                            if (mLatLng.latitude <= 0 || mLatLng.longitude <= 0)
                                return;
                            if (positionMarker == null) {
                                positionMarker = showPoint(
                                        mLatLng,
                                        intent.getStringExtra("city"),
                                        intent.getStringExtra("address"));
                            } else {
                                updateMarker(positionMarker,
                                        mLatLng,
                                        intent.getStringExtra("city"),
                                        intent.getStringExtra("address"));
                            }
                            if (is_first_show) {
                                CameraUpdate cameraUpdate = CameraUpdateFactory.newCameraPosition(new CameraPosition(positionMarker.getPosition(),mMap.getCameraPosition().zoom,0,0));
                                mMap.animateCamera(cameraUpdate);
                                is_first_show = false;
                            }
                        } else {
                            Toast.makeText(PositionActivity.this, intent.getStringExtra("errinfo"), Toast.LENGTH_LONG).show();
                        }
                    }
                }
            };
            IntentFilter intentFilter = new IntentFilter();
            // 2. 设置接收广播的类型
            intentFilter.addAction(PositionService.ACTION_LOCATION);
            // 3. 动态注册：调用Context的registerReceiver（）方法
            registerReceiver(mBroadcastReceiver, intentFilter);
        }
    }

    boolean quiteState = false;
    @Override
    public void onBackPressed() {
        if (quiteState) {
            stopAlarm();
            finish();
        } else {
            Toast.makeText(this, "再按一次退出程序", Toast.LENGTH_LONG).show();
            quiteState = true;
            runDelay(new Runnable() {
                @Override
                public void run() {
                    quiteState = false;
                }
            }, 3000);
        }
    }

    private void runDelay(final Runnable runnable, final long delay) {
        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    Thread.sleep(delay);
                } catch (InterruptedException e) {}
                runOnUiThread(runnable);
            }
        }).start();
    }

    private void showTextOnUIThread(final String message) {
        this.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                Toast.makeText(PositionActivity.this, message, Toast.LENGTH_LONG).show();
            }
        });
    }

    Map<String, Bitmap> iconMap = new HashMap<>();
    private void initIcons() {
        Bitmap bitmap = BitmapFactory.decodeResource(getResources(),R.mipmap.sprite);

        double xScale = bitmap.getWidth() / 460.0;
        double yScale = bitmap.getHeight() / 1964.0;
        int size = (int)(55 * xScale);
        iconMap.put("position", Bitmap.createBitmap(bitmap, 0, (int)(yScale * 1375.0), size, size));
        iconMap.put("person", Bitmap.createBitmap(bitmap, (int)(335 * xScale), (int)(yScale * 1490), size, size));
        iconMap.put("dest", Bitmap.createBitmap(bitmap, 0, (int)(yScale * 650), size, size));
        iconMap.put("dest1", Bitmap.createBitmap(bitmap, (int)(220 * xScale), (int)(yScale * 440), size, size));

        bitmap.recycle();
    }

    private Marker showPoint(LatLng latLng, String city, String address, String iconName) {
        MarkerOptions markerOption = new MarkerOptions();
        markerOption.position(latLng);
        markerOption.title(city).snippet(address);

        markerOption.draggable(true);//设置Marker可拖动
        markerOption.icon(BitmapDescriptorFactory.fromBitmap(iconMap.get(iconName)));
        // 将Marker设置为贴地显示，可以双指下拉地图查看效果
        markerOption.setFlat(true);//设置marker平贴地图效果

        return mMap.addMarker(markerOption);
    }

    private Marker showPoint(LatLng latLng, String city, String address) {
        return showPoint(latLng, city, address, "person");
    }

    private void updateMarker(Marker marker, LatLng latLng, String city, String address) {
        marker.setPosition(latLng);
        marker.setTitle(city);
        marker.setSnippet(address);
    }

    private void showPosition(JSONArray points) {
        for (int idx = 0; idx < points.size(); idx ++) {
            JSONObject point = points.getJSONObject(idx);
            System.out.println(point);
            showPoint(new LatLng(point.getDouble("latitude"), point.getDouble("longitude")), null, null, "dest1");
        }
    }

    private void requestLocationPrivage() {
        LocationManager locationManager = (LocationManager) getSystemService(LOCATION_SERVICE);
        if (locationManager.isProviderEnabled(LocationManager.GPS_PROVIDER)) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.ACCESS_COARSE_LOCATION}, LOCATION_CODE);
            } else {
                startAlarm();
            }
        } else {
            Toast.makeText(this, "系统检测到未开启GPS定位服务", Toast.LENGTH_SHORT).show();
            Intent intent = new Intent();
            intent.setAction(Settings.ACTION_LOCATION_SOURCE_SETTINGS);
            startActivityForResult(intent, 1315);
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        switch (requestCode) {
            case LOCATION_CODE: {
                if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                    // 权限被用户同意。
                    startAlarm();
                } else {
                    // 权限被用户拒绝了。
                    Toast.makeText(this, "定位权限被禁止，相关地图功能无法使用！",Toast.LENGTH_LONG).show();
                }

            }
        }
    }
}
