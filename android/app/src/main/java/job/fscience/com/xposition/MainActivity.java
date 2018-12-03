package job.fscience.com.xposition;

import android.content.Intent;
import android.graphics.Color;
import android.graphics.drawable.Drawable;
import android.os.Handler;
import android.os.Bundle;
import android.util.Log;
import android.util.Pair;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.view.Window;
import android.widget.*;
import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import com.amap.api.maps.AMap;
import com.amap.api.maps.CameraUpdate;
import com.amap.api.maps.CameraUpdateFactory;
import com.amap.api.maps.MapView;
import com.amap.api.maps.model.*;
import com.amap.api.maps.utils.SpatialRelationUtil;
import com.amap.api.maps.utils.overlay.SmoothMoveMarker;
import job.fscience.com.lib.AuthCallback;
import job.fscience.com.lib.BaseActivity;
import job.fscience.com.lib.MapMarkManager;
import job.fscience.com.lib.SlidingUpPanelLayout;
import okhttp3.Call;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class MainActivity extends BaseActivity implements CompoundButton.OnCheckedChangeListener {
    private static final String TAG = "DemoActivity";
    public static final String SAVED_STATE_ACTION_BAR_HIDDEN = "saved_state_action_bar_hidden";
    private SlidingUpPanelLayout mLayout;
    private AMap mMap;
    private UserListAdapter adapter;

    private Polyline polyline = null;
    private MapMarkManager markManager = null;

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
        markManager = new MapMarkManager(this, mMap);

        ((TextView) findViewById(R.id.head)).setText(
                XApplication.userInfo.getString("nickname") +
                        "(" + XApplication.examInfo.getString("name") + ")");

        mLayout = (SlidingUpPanelLayout) findViewById(R.id.sliding_layout);
        mLayout.setPanelSlideListener(new SlidingUpPanelLayout.PanelSlideListener() {
            @Override
            public void onPanelSlide(View panel, float slideOffset) {
//                Log.i(TAG, "onPanelSlide, offset " + slideOffset);
            }

            @Override
            public void onPanelExpanded(View panel) {
                Log.i(TAG, "onPanelExpanded");

                ListView listView = (ListView) findViewById(R.id.user_list);
                LinearLayout.LayoutParams params = (LinearLayout.LayoutParams)listView.getLayoutParams();
                params.height = panel.getHeight() - panel.getTop() - listView.getTop();
                listView.setLayoutParams(params);
            }

            @Override
            public void onPanelCollapsed(View panel) {
                Log.i(TAG, "onPanelCollapsed");
//                ListView listView = (ListView) findViewById(R.id.user_list);
//                listView.clearChoices();
//                listView.invalidateViews();
            }

            @Override
            public void onPanelAnchored(View panel) {
                Log.i(TAG, "onPanelAnchored");

                ListView listView = (ListView) findViewById(R.id.user_list);
                LinearLayout.LayoutParams params = (LinearLayout.LayoutParams)listView.getLayoutParams();
                params.height = panel.getHeight() - panel.getTop() - listView.getTop();
                listView.setLayoutParams(params);
            }
        });
        mLayout.setAnchorPoint(0.5f);//用来测试锚点功能

        XApplication.getServerInstance().managerGetExam(new AuthCallback() {
            @Override
            public void onFailureEx(Call call, IOException e) {
                showTextOnUIThread("网络问题");
            }

            @Override
            public void onResponseEx(JSONObject data) throws IOException {
                if (data == null) {
                    showTextOnUIThread("服务器问题");
                } else if (data.getInteger("state") == 1) {
                    data.getJSONArray("positions");
                    System.out.println(data);
                } else {
                    showTextOnUIThread(data.getString("message"));
                }
            }
        });

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

//        XApplication.getServerInstance().managerGetExam(new AuthCallback() {
//            @Override
//            public void onFailureEx(Call call, IOException e) {
//                showTextOnUIThread("网络问题");
//            }
//
//            @Override
//            public void onResponseEx(final JSONObject data) throws IOException {
//                if (data == null) {
//                    showTextOnUIThread("服务器问题");
//                } else if (data.getInteger("state") == 1) {
//                    runOnUiThread(new Runnable() {
//                        @Override
//                        public void run() {
//                            adapter.updateData(data.getJSONArray("users"));
//                            showPosition(data.getJSONArray("users"));
//                        }
//                    });
//
//                } else {
//                    showTextOnUIThread(data.getString("message"));
//                }
//            }
//        });
        XApplication.getServerInstance().managerGetExamUsers(XApplication.examInfo.getInteger("id"), new AuthCallback() {
            @Override
            public void onFailureEx(Call call, IOException e) {
                showTextOnUIThread("网络问题");
            }

            @Override
            public void onResponseEx(final JSONObject data) throws IOException {
                if (data == null) {
                    showTextOnUIThread("服务器问题");
                } else if (data.getInteger("state") == 1) {
                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            adapter.updateData(data.getJSONArray("users"));
//                            showPosition(data.getJSONArray("users"));
                        }
                    });

                } else {
                    showTextOnUIThread(data.getString("message"));
                }
            }
        });

        findViewById(R.id.delete).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                unSelectUser(true);
            }
        });
        findViewById(R.id.route).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if (polyline != null) {
                    polyline.remove();
                }

                XApplication.getServerInstance().managerGetUserTrack(((int) view.getTag()), new AuthCallback() {
                    @Override
                    public void onFailureEx(Call call, IOException e) {
                        showTextOnUIThread("网络问题");
                    }

                    @Override
                    public void onResponseEx(final JSONObject object) throws IOException {
                        if (object == null) {
                            showTextOnUIThread("服务器问题");
                        } else if (object.getInteger("state") == 1) {
                            runOnUiThread(new Runnable() {
                                @Override
                                public void run() {
                                    try {
                                        JSONArray points = object.getJSONArray("points");
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
                        } else {
                            showTextOnUIThread(object.getString("message"));
                        }
                    }
                });
            }
        });
        findViewById(R.id.attribute).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if (selectedUserId == -1) {
                    Intent intent = new Intent(MainActivity.this, UsersActivity.class);
                    startActivity(intent);
                } else {
                    Intent intent = new Intent(MainActivity.this, AttributeActivity.class);
                    intent.putExtra(AttributeActivity.ACTIVE_USER_ID, selectedUserId);
                    startActivity(intent);
                }
            }
        });
        findViewById(R.id.play).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
//                startPlay();
                final AnimationSettingDialog dialog = new AnimationSettingDialog(MainActivity.this);
                dialog.show();
                dialog.setCallback(new AnimationSettingDialog.AnimationSettingClick() {
                    @Override
                    public void onConfirmClick() {
                        startPlay(dialog.getMinValue(), dialog.getMaxValue());
                    }
                });
            }
        });

        updatePosition();
    }

    Handler mHandler = new Handler();
    private void updatePosition() {
        mHandler.postDelayed(new Runnable() {
            @Override
            public void run() {
                XApplication.getServerInstance().managerGetLocations( new AuthCallback() {
                    @Override
                    public void onFailureEx(Call call, IOException e) {
                        showTextOnUIThread("网络问题");
                        updatePosition();
                    }

                    @Override
                    public void onResponseEx(final JSONObject object) throws IOException {
                        if (object == null) {
                            showTextOnUIThread("服务器问题");
                        } else if (object.getInteger("state") == 1) {
                            runOnUiThread(new Runnable() {
                                @Override
                                public void run() {
                                    try {
                                        showPosition(object.getJSONArray("locations"));
                                    } catch (Exception e) {}
                                }
                            });
                        } else {
                            showTextOnUIThread(object.getString("message"));
                        }
                        updatePosition();
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
                holder.userIdTextView =  view.findViewById(R.id.user_id);
                holder.userNameTextView = view.findViewById(R.id.user_name);
                holder.departNameTextView = view.findViewById(R.id.user_depart);
                holder.userStateButtom = view.findViewById(R.id.state);
                holder.userStateButtom.setOnCheckedChangeListener(MainActivity.this);
                view.setTag(holder);
                viewHolder = holder;
            }else{
                viewHolder = (UserInfoViewHolder) convertView.getTag();
            }

            JSONObject object = data.getJSONObject(i);
            viewHolder.userIdTextView.setText(object.getString("id"));
            viewHolder.userNameTextView.setText(object.getString("username"));
            viewHolder.departNameTextView.setText(object.getString("departname"));

            Boolean visible = markManager.userVisibleMap.get(object.getInteger("id"));
            viewHolder.userStateButtom.setChecked(visible == null || visible);
            viewHolder.userStateButtom.setTag(object.getInteger("id"));

            return view;
        }
    }

    class UserInfoViewHolder {
        public TextView userIdTextView;
        public TextView userNameTextView;
        public TextView departNameTextView;
        public ToggleButton userStateButtom;
    }

    private void showPosition(JSONArray points) {
        for (int idx = 0; idx < points.size(); idx ++) {
            JSONObject point = points.getJSONObject(idx);

            markManager.updateUser(
                    point.getInteger("user_id"),
                    point.getString("username"),
                    point.getDouble("latitude"),
                    point.getDouble("longitude"),
                    point.getInteger("state"));
        }
    }

    private void startAnimation(int id) {
        Marker marker = markManager.animationMark(id);
        if (marker != null) {
            CameraUpdate cameraUpdate = CameraUpdateFactory.newCameraPosition(new CameraPosition(marker.getPosition(), 14, 0, 0));
            mMap.moveCamera(cameraUpdate);
        }
    }

    private int selectedUserId = -1;
    private void selectUser(int userId) {
        unSelectUser(false);

        if (markManager.userValidate(userId)) {
            findViewById(R.id.route).setVisibility(View.VISIBLE);
//            findViewById(R.id.attribute).setVisibility(View.VISIBLE);
            findViewById(R.id.delete).setVisibility(View.VISIBLE);
            findViewById(R.id.play).setVisibility(View.VISIBLE);
            findViewById(R.id.route).setTag(userId);
            findViewById(R.id.delete).setTag(userId);

            startAnimation(userId);
            selectedUserId = userId;
        } else {
            Toast.makeText(this, "当前员工未定位", Toast.LENGTH_SHORT).show();
        }
    }
    private void unSelectUser(boolean clear) {
        if (polyline != null) {
            polyline.remove();
        }
        stopPlay();

        findViewById(R.id.route).setVisibility(View.GONE);
//        findViewById(R.id.attribute).setVisibility(View.GONE);
        findViewById(R.id.delete).setVisibility(View.GONE);
        findViewById(R.id.play).setVisibility(View.GONE);
        if (clear) {
            ((ListView) findViewById(R.id.user_list)).clearChoices();
            ((ListView) findViewById(R.id.user_list)).invalidateViews();
        }
        selectedUserId = -1;
    }

    SmoothMoveMarker smoothMarker = null;
    private void startPlay(float minVlaue, float maxValue) {
        stopPlay();

        if (polyline != null) {
            List<LatLng> xpoints = polyline.getPoints();
            List<LatLng> points = new ArrayList<>();
            for (int idx = (int) ((xpoints.size() / 100) * minVlaue); idx < (int) ((xpoints.size() / 100) * maxValue); idx ++) {
                points.add(xpoints.get(idx));
            }
            LatLngBounds bounds = new LatLngBounds(points.get(0), points.get(points.size() - 2));
            mMap.animateCamera(CameraUpdateFactory.newLatLngBounds(bounds, 50));

            smoothMarker = new SmoothMoveMarker(mMap);
            // 设置滑动的图标
//            smoothMarker.setDescriptor(BitmapDescriptorFactory.fromBitmap(iconMap.get("dest")));

            LatLng drivePoint = points.get(0);
            Pair<Integer, LatLng> pair = SpatialRelationUtil.calShortestDistancePoint(points, drivePoint);
            points.set(pair.first, drivePoint);
            List<LatLng> subList = points.subList(pair.first, points.size());

            // 设置滑动的轨迹左边点
            smoothMarker.setPoints(subList);
            // 设置滑动的总时间
            smoothMarker.setTotalDuration((int) (40 * ((maxValue - minVlaue) / 100)));
            // 开始滑动
            smoothMarker.startSmoothMove();

            smoothMarker.setMoveListener(new SmoothMoveMarker.MoveListener() {
                @Override
                public void move(double v) {
                    System.out.println(v);
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

    private void showTextOnUIThread(final String message) {
        this.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                Toast.makeText(MainActivity.this, message, Toast.LENGTH_LONG).show();
            }
        });
    }

    @Override
    public void onCheckedChanged(CompoundButton compoundButton, boolean checked) {
        Integer userId = (Integer)compoundButton.getTag();
        markManager.setVisible(userId, checked);
    }
}
