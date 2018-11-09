package job.fscience.com.xposition;

import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.ListView;
import android.widget.TextView;
import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.Response;

import java.io.IOException;

public class AttributeActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_attribute);

        ListView listView = (ListView) findViewById(R.id.attribute);
        final AttributeAdapter adapter = new AttributeAdapter();
        listView.setAdapter(adapter);

        XApplication.getServerInstance().getExamResult(1, new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {

            }

            @Override
            public void onResponse(Call call, final Response response) throws IOException {
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        try {
                            JSONObject points = JSON.parseObject(response.body().string());
                            adapter.updateData(points.getJSONArray("points"));
                        } catch (Exception e) {}
                    }
                });

            }
        });
    }

    class AttributeAdapter extends BaseAdapter {
        JSONArray data;

        public void updateData(JSONArray data) {
            this.data = data;
            notifyDataSetChanged();
        }

        @Override
        public int getCount() {
            if (data == null)
                return 0;
            return data.size();
        }

        @Override
        public Object getItem(int i) {
            if (data == null)
                return null;
            return data.getJSONObject(i);
        }

        @Override
        public long getItemId(int i) {
            return i;
        }

        @Override
        public View getView(int i, View convertView, ViewGroup viewGroup) {
            LayoutInflater inflater = AttributeActivity.this.getLayoutInflater();
            View view = convertView;
            AttributeActivity.AttributeViewHolder viewHolder;
            if (convertView==null) {
                view = inflater.inflate(R.layout.item_user_attribute, null);
                AttributeActivity.AttributeViewHolder holder = new AttributeActivity.AttributeViewHolder();
                holder.numberTextView = (TextView) view.findViewById(R.id.number);
                holder.latitudeTextView = (TextView) view.findViewById(R.id.latitude);
                holder.longitudeTextView = (TextView) view.findViewById(R.id.longitude);
                holder.weightTextView = (TextView) view.findViewById(R.id.weight);
                holder.scoreTextView = (TextView) view.findViewById(R.id.score);
                view.setTag(holder);
                viewHolder = holder;
            }else{
                viewHolder = (AttributeActivity.AttributeViewHolder) convertView.getTag();
            }

            JSONObject value = data.getJSONObject(i);
            viewHolder.latitudeTextView.setText("" + value.getDouble("latitude"));
            viewHolder.longitudeTextView.setText("" + value.getDouble("longitude"));
            viewHolder.numberTextView.setText("" + value.getInteger("id"));
            viewHolder.weightTextView.setText("" + value.getDouble("weight"));
            viewHolder.scoreTextView.setText("" + value.getDouble("score"));

            return view;
        }
    }

    class AttributeViewHolder {
        public TextView numberTextView;
        public TextView latitudeTextView;
        public TextView longitudeTextView;
        public TextView weightTextView;
        public TextView scoreTextView;
    }
}
