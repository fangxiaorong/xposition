package job.fscience.com.xposition;

import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Color;
import android.graphics.drawable.Drawable;
import android.os.Handler;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.util.Pair;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.view.Window;
import android.view.animation.LinearInterpolator;
import android.widget.*;
import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import com.amap.api.maps.AMap;
import com.amap.api.maps.CameraUpdate;
import com.amap.api.maps.CameraUpdateFactory;
import com.amap.api.maps.MapView;
import com.amap.api.maps.model.*;
import com.amap.api.maps.model.animation.Animation;
import com.amap.api.maps.model.animation.RotateAnimation;
import com.amap.api.maps.utils.SpatialRelationUtil;
import com.amap.api.maps.utils.overlay.SmoothMoveMarker;
import job.fscience.com.lib.SlidingUpPanelLayout;
import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.Response;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class MainActivity extends AppCompatActivity {
    private static final String TAG = "DemoActivity";
    public static final String SAVED_STATE_ACTION_BAR_HIDDEN = "saved_state_action_bar_hidden";
    private SlidingUpPanelLayout mLayout;
    private AMap mMap;
    private UserListAdapter adapter;

    private Polyline polyline = null;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().requestFeature(Window.FEATURE_ACTION_BAR_OVERLAY);
        setContentView(R.layout.activity_demo);

        final MapView mapView = (MapView) findViewById(R.id.map);
        mapView.onCreate(savedInstanceState);// 此方法必须重写
        mMap = mapView.getMap();
        mMap.setTrafficEnabled(false);// 显示实时交通状况
        //地图模式可选类型：MAP_TYPE_NORMAL,MAP_TYPE_SATELLITE,MAP_TYPE_NIGHT
        mMap.setMapType(AMap.MAP_TYPE_NORMAL);

        mLayout = (SlidingUpPanelLayout) findViewById(R.id.sliding_layout);
        mLayout.setPanelSlideListener(new SlidingUpPanelLayout.PanelSlideListener() {
            @Override
            public void onPanelSlide(View panel, float slideOffset) {
//                Log.i(TAG, "onPanelSlide, offset " + slideOffset);
            }

            @Override
            public void onPanelExpanded(View panel) {
                Log.i(TAG, "onPanelExpanded");

            }

            @Override
            public void onPanelCollapsed(View panel) {
                Log.i(TAG, "onPanelCollapsed");
                ListView listView = (ListView) findViewById(R.id.user_list);
                listView.clearChoices();
                listView.invalidateViews();
            }

            @Override
            public void onPanelAnchored(View panel) {
                Log.i(TAG, "onPanelAnchored");
            }
        });
        mLayout.setAnchorPoint(0.5f);//用来测试锚点功能

        XApplication.getServerInstance().getExamLine(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
            }

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                JSONObject data = (JSONObject) JSON.parse(response.body().string());
                data.getJSONArray("positions");
                System.out.println(data);
            }
        });

        ///
        initIcons();
        // 格式设置
        TextView headTextView = (TextView)findViewById(R.id.head);
        Drawable headDrawable = getResources().getDrawable(R.mipmap.ic_launcher);
        headDrawable.setBounds(0, 0, 60, 60);
        headTextView.setCompoundDrawables(headDrawable, null, null, null);


        adapter = new UserListAdapter();
        final ListView listView = (ListView) findViewById(R.id.user_list);
        listView.setAdapter(adapter);
        listView.setChoiceMode(ListView.CHOICE_MODE_SINGLE);
        listView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> adapterView, View view, int i, long itemId) {
                selectUser((int) itemId);
            }
        });

        JSONObject data = (JSONObject) JSON.parse(getIntent().getStringExtra("data"));
        adapter.updateData(data.getJSONArray("users"));

        findViewById(R.id.delete).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                unSelectUser();
            }
        });
        findViewById(R.id.route).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if (polyline != null) {
                    polyline.remove();
                }

                XApplication.getServerInstance().getExamUserPos(((int) view.getTag()), new Callback() {
                    @Override
                    public void onFailure(Call call, IOException e) {
                        //
                    }

                    @Override
                    public void onResponse(Call call, final Response response) throws IOException {
                        runOnUiThread(new Runnable() {
                            @Override
                            public void run() {
                                try {
                                    JSONObject data = JSON.parseObject(response.body().string());
                                    JSONArray points = data.getJSONArray("points");
                                    List<LatLng> latLngs = new ArrayList<>();
                                    for (int idx = 0; idx < points.size(); idx ++) {
                                        JSONObject point = points.getJSONObject(idx);
                                        latLngs.add(new LatLng(point.getDouble("latitude"), point.getDouble("longitude")));
                                    }
                                    polyline = mapView.getMap().addPolyline(new PolylineOptions().
                                            addAll(latLngs).width(10).color(Color.argb(255, 1, 1, 1)));
                                } catch (Exception e) {}
                            }
                        });
                    }
                });
            }
        });
        findViewById(R.id.attribute).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(MainActivity.this, AttributeActivity.class);
                startActivity(intent);
            }
        });
        findViewById(R.id.play).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                startPlay();
            }
        });

        udpatePosition();
    }

    Handler mHandler = new Handler();
    private void udpatePosition() {
        mHandler.postDelayed(new Runnable() {
            @Override
            public void run() {
                XApplication.getServerInstance().getExamUsersPos(1, new Callback() {
                    @Override
                    public void onFailure(Call call, IOException e) {
                        runOnUiThread(new Runnable() {
                            @Override
                            public void run() {
                                Toast.makeText(MainActivity.this, "网络问题", Toast.LENGTH_SHORT).show();
                                udpatePosition();
                            }
                        });
                    }

                    @Override
                    public void onResponse(Call call, final Response response) throws IOException {
                        runOnUiThread(new Runnable() {
                            @Override
                            public void run() {
                                try {
                                    JSONObject object = (JSONObject) JSON.parse(response.body().string());
                                    showPosition(object.getJSONArray("users"));
                                } catch (Exception e) {}
                                udpatePosition();
                            }
                        });
                    }
                });
            }
        }, 3000);
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
        outState.putBoolean(SAVED_STATE_ACTION_BAR_HIDDEN, mLayout.isExpanded());
    }

    @Override
    public void onBackPressed() {
        if(mLayout != null && mLayout.isExpanded()) {
            mLayout.collapsePane();
        } else {
            super.onBackPressed();
        }
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
        iconMap.put("delete", Bitmap.createBitmap(bitmap, (int)(220 * xScale), (int)(yScale * 590), size, size));

        bitmap.recycle();
    }

    class UserListAdapter extends BaseAdapter {
        JSONArray data = null;
        public void updateData(JSONArray data) {
            this.data = data;
            this.notifyDataSetChanged();
        }
        @Override
        public int getCount() {
            if (data == null)
                return 0;
            return data.size();
        }

        @Override
        public Object getItem(int idx) {
            if (data == null)
                return null;
            return data.getJSONObject(idx);
        }

        @Override
        public long getItemId(int idx) {
            if (data == null)
                return -1;
            return data.getJSONObject(idx).getInteger("id");
        }

        @Override
        public View getView(int i, View convertView, ViewGroup viewGroup) {
            LayoutInflater inflater = MainActivity.this.getLayoutInflater();
            View view = convertView;
            UserInfoViewHolder viewHolder;
            if (convertView==null) {
                view = inflater.inflate(R.layout.item_user_info, null);
                UserInfoViewHolder holder = new UserInfoViewHolder();
                holder.userIdTextView = (TextView) view.findViewById(R.id.user_id);
                holder.userNameTextView = (TextView) view.findViewById(R.id.user_name);
                holder.userScoreTextView = (TextView) view.findViewById(R.id.user_score);
                view.setTag(holder);
                viewHolder = holder;
            }else{
                viewHolder = (UserInfoViewHolder) convertView.getTag();
            }

            JSONObject object = data.getJSONObject(i);
            viewHolder.userIdTextView.setText(object.getString("id"));
            viewHolder.userNameTextView.setText(object.getString("name"));
            viewHolder.userScoreTextView.setText(object.getString("score"));

            return view;
        }
    }

    class UserInfoViewHolder {
        public TextView userIdTextView;
        public TextView userNameTextView;
        public TextView userScoreTextView;
    }

    Map<Integer, Marker> userMap = new HashMap<>();
    private void showPosition(JSONArray points) {
        for (int idx = 0; idx < points.size(); idx ++) {
            JSONObject point = points.getJSONObject(idx);
            System.out.println(userMap.size());
            Marker marker = userMap.get(point.getInteger("id"));
            if (marker == null) {
                System.out.println(point);
                MarkerOptions markerOption = new MarkerOptions();
                markerOption.position(new LatLng(point.getDouble("latitude"), point.getDouble("longitude")));
                markerOption.title(null).snippet(null);

                markerOption.draggable(true);//设置Marker可拖动
                markerOption.icon(BitmapDescriptorFactory.fromBitmap(iconMap.get("person")));
                // 将Marker设置为贴地显示，可以双指下拉地图查看效果
                markerOption.setFlat(true);//设置marker平贴地图效果
                userMap.put(point.getInteger("id"), mMap.addMarker(markerOption));
            } else {
                System.out.println("xxxxx:" + point);
                marker.setPosition(new LatLng(point.getDouble("latitude"), point.getDouble("longitude")));
            }
        }
    }

    private void startAnimation(int id) {
        Animation animation = new RotateAnimation(0,360,0,0, 0);
        long duration = 1000L;
        animation.setDuration(duration);
        animation.setInterpolator(new LinearInterpolator());

        Marker animationMark = userMap.get(id);
        animationMark.setAnimation(animation);
        animationMark.startAnimation();

        CameraUpdate cameraUpdate = CameraUpdateFactory.newCameraPosition(new CameraPosition(animationMark.getPosition(),14,0,0));
        mMap.moveCamera(cameraUpdate);
    }

    private void selectUser(int userId) {
        findViewById(R.id.route).setVisibility(View.VISIBLE);
        findViewById(R.id.attribute).setVisibility(View.VISIBLE);
        findViewById(R.id.delete).setVisibility(View.VISIBLE);
        findViewById(R.id.play).setVisibility(View.VISIBLE);
        findViewById(R.id.route).setTag(userId);
        findViewById(R.id.delete).setTag(userId);

        startAnimation(userId);
    }
    private void unSelectUser() {
        if (polyline != null) {
            polyline.remove();
        }
        stopPlay();

        findViewById(R.id.route).setVisibility(View.GONE);
        findViewById(R.id.attribute).setVisibility(View.GONE);
        findViewById(R.id.delete).setVisibility(View.GONE);
        findViewById(R.id.play).setVisibility(View.GONE);
        ((ListView)findViewById(R.id.user_list)).clearChoices();
        ((ListView)findViewById(R.id.user_list)).invalidateViews();
    }

    SmoothMoveMarker smoothMarker = null;
    private void startPlay() {
        if (polyline != null) {
            List<LatLng> points = polyline.getPoints();
            LatLngBounds bounds = new LatLngBounds(points.get(0), points.get(points.size() - 2));
            mMap.animateCamera(CameraUpdateFactory.newLatLngBounds(bounds, 50));

            smoothMarker = new SmoothMoveMarker(mMap);
            // 设置滑动的图标
            smoothMarker.setDescriptor(BitmapDescriptorFactory.fromBitmap(iconMap.get("dest")));

            LatLng drivePoint = points.get(0);
            Pair<Integer, LatLng> pair = SpatialRelationUtil.calShortestDistancePoint(points, drivePoint);
            points.set(pair.first, drivePoint);
            List<LatLng> subList = points.subList(pair.first, points.size());

            // 设置滑动的轨迹左边点
            smoothMarker.setPoints(subList);
            // 设置滑动的总时间
            smoothMarker.setTotalDuration(40);
            // 开始滑动
            smoothMarker.startSmoothMove();

            smoothMarker.setMoveListener(new SmoothMoveMarker.MoveListener() {
                @Override
                public void move(double v) {
                    if (v <= 0) {
                        stopPlay();
                    }
                }
            });
        }
    }

    private void stopPlay() {
        if (smoothMarker != null) {
            smoothMarker.stopMove();
            smoothMarker.removeMarker();
            smoothMarker = null;
        }
    }
}
