package job.fscience.com.xposition;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.BaseAdapter;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;

import java.io.IOException;

import job.fscience.com.lib.AuthCallback;
import job.fscience.com.lib.BaseActivity;
import okhttp3.Call;

public class LineInfoActivity extends BaseActivity {
    PointListAdapter adapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_line_info);

        ListView pointListView = (ListView) findViewById(R.id.point_list);
        adapter = new PointListAdapter();
        pointListView.setAdapter(adapter);
        pointListView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> adapterView, View view, int i, long l) {
                Intent intent = new Intent(LineInfoActivity.this, PointInfoActivity.class);
                intent.putExtra("info", JSONObject.toJSONString(adapter.getItem(i)));
                intent.putExtra("index", i);
                startActivity(intent);
            }
        });

        findViewById(R.id.add_button).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(LineInfoActivity.this, PointInfoActivity.class);
                startActivity(intent);
            }
        });

        loadLineInfo(getIntent().getLongExtra("lineId", -1L));
    }

    private void loadLineInfo (long lineId) {
        if (lineId <= 0) return;
        XApplication.getServerInstance().adminGetExamLine((int)lineId, new AuthCallback() {
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
                            updateInfo(data.getJSONObject("exam_line"));
                        }
                    });
                } else {
                    showTextOnUIThread(data.getString("message"));
                }
            }
        });
    }

    private void updateInfo(JSONObject info) {
        ((TextView) findViewById(R.id.tv_title)).setText(info.getString("name"));
        JSONArray points = JSONArray.parseArray(info.getString("points"));
        adapter.updateDate(points);
    }

    private void showTextOnUIThread(final String message) {
        this.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                Toast.makeText(LineInfoActivity.this, message, Toast.LENGTH_LONG).show();
            }
        });
    }

    class PointListAdapter extends BaseAdapter {
        JSONArray points = null;

        public void updateDate(JSONArray points) {
            this.points = points;
            this.notifyDataSetChanged();
        }

        @Override
        public int getCount() {
            if (points == null)
                return 0;
            return points.size();
        }

        @Override
        public Object getItem(int i) {
            if (points == null)
                return null;
            return points.get(i);
        }

        @Override
        public long getItemId(int i) {
            return i;
        }

        @Override
        public View getView(int i, View convertView, ViewGroup viewGroup) {
            View view = convertView;
            PointInfoHolder viewHolder;
            if (convertView==null) {
                view = LineInfoActivity.this.getLayoutInflater().inflate(R.layout.item_point_info, null);
                PointInfoHolder holder = new PointInfoHolder();
                holder.indexView =  view.findViewById(R.id.index_text);
                holder.xView = view.findViewById(R.id.x_text);
                holder.yView = view.findViewById(R.id.y_text);
                holder.distanceView = view.findViewById(R.id.distance_text);
                holder.weightView = view.findViewById(R.id.weight_text);
                holder.startView = view.findViewById(R.id.start_text);
                holder.endView = view.findViewById(R.id.end_text);
                view.setTag(holder);
                viewHolder = holder;
            } else {
                viewHolder = (PointInfoHolder) convertView.getTag();
            }

            JSONObject point = points.getJSONObject(i);
            viewHolder.indexView.setText("" + (i + 1));
            viewHolder.xView.setText("X: " + point.getString("x"));
            viewHolder.yView.setText("Y: " + point.getString("y"));
            viewHolder.weightView.setText("权重: " + point.getString("weight"));
            viewHolder.distanceView.setText("最大距离: " + point.getString("maxdistance"));
            viewHolder.startView.setText("开始时间: " + point.getString("stime"));
            viewHolder.endView.setText("结束时间: " + point.getString("etime"));

            return view;
        }
    }

    class PointInfoHolder {
        TextView indexView;
        TextView xView;
        TextView yView;
        TextView weightView;
        TextView distanceView;
        TextView startView;
        TextView endView;
    }
}
