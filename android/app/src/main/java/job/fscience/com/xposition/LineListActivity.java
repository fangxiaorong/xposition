package job.fscience.com.xposition;

import android.content.Intent;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.*;
import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import job.fscience.com.lib.AuthCallback;
import job.fscience.com.lib.BaseActivity;
import okhttp3.Call;

import java.io.IOException;

public class LineListActivity extends BaseActivity {
    LineListAdapter adapter;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_line_list);

        findViewById(R.id.add).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {

            }
        });

        ListView listView = (ListView) findViewById(R.id.line_list_view);
        adapter = new LineListAdapter();
        listView.setAdapter(adapter);
        listView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> adapterView, View view, int i, long id) {
                Intent intent = new Intent(LineListActivity.this, LineInfoActivity.class);
                intent.putExtra("lineId", id);
                startActivity(intent);
            }
        });
        reloadLines();
    }

    private void reloadLines () {
        XApplication.getServerInstance().adminGetExamLines(new AuthCallback() {
            @Override
            public void onFailureEx(Call call, IOException e) {
                showTextOnUIThread("网络问题");
            }

            @Override
            public void onResponseEx(JSONObject data) throws IOException {
                if (data == null) {
                    showTextOnUIThread("服务器问题");
                } else if (data.getInteger("state") == 1) {
                    adapter.updateData(data.getJSONArray("exam_line"));
                } else {
                    showTextOnUIThread(data.getString("message"));
                }
            }
        });
    }

    class LineListAdapter extends BaseAdapter {
        JSONArray lines = null;

        public void updateData(JSONArray lines) {
            this.lines = lines;
            this.notifyDataSetChanged();
        }

        @Override
        public int getCount() {
            if (this.lines == null)
                return 0;
            return this.lines.size();
        }

        @Override
        public Object getItem(int i) {
            if (this.lines == null)
                return null;
            return this.lines.get(i);
        }

        @Override
        public long getItemId(int i) {
            if (this.lines == null)
                return 0;
            return this.lines.getJSONObject(i).getInteger("id");
        }

        @Override
        public View getView(int i, View convertView, ViewGroup viewGroup) {
            View view = convertView;
            LineViewHolder viewHolder;
            if (convertView==null) {
                view = LineListActivity.this.getLayoutInflater().inflate(R.layout.item_line_info, null);
                LineViewHolder holder = new LineViewHolder();
                holder.validateImageView =  view.findViewById(R.id.state_image);
                holder.nameTextView = view.findViewById(R.id.name_text);
                view.setTag(holder);
                viewHolder = holder;
            } else{
                viewHolder = (LineViewHolder) convertView.getTag();
            }

            JSONObject line = this.lines.getJSONObject(i);
            if (line.getInteger("valid") == 1) { // 有效
                viewHolder.validateImageView.setImageResource(R.mipmap.favoriteon);
            } else {
                viewHolder.validateImageView.setImageResource(R.mipmap.favoriteoff);
            }
            viewHolder.nameTextView.setText(line.getString("name"));

            return view;
        }
    }

    private void showTextOnUIThread(final String message) {
        this.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                Toast.makeText(LineListActivity.this, message, Toast.LENGTH_LONG).show();
            }
        });
    }

    class LineViewHolder {
        ImageView validateImageView;
        TextView nameTextView;
    }
}
