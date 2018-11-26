package job.fscience.com.xposition;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;
import com.alibaba.fastjson.JSONObject;
import job.fscience.com.lib.AuthCallback;
import job.fscience.com.lib.BaseActivity;
import okhttp3.Call;

import java.io.IOException;

public class UsersActivity extends BaseActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_users);

        ListView userListView = (ListView)findViewById(R.id.user_list);
        UsersAdapter adapter = new UsersAdapter();
        userListView.setAdapter(adapter);

        findViewById(R.id.calculate).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                reCalculate();
            }
        });
        findViewById(R.id.export).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {

            }
        });
    }

    private void showTextOnUIThread(final String message) {
        this.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                Toast.makeText(UsersActivity.this, message, Toast.LENGTH_LONG).show();
            }
        });
    }
    private void reCalculate() {
        double level1, level2, level3, level4;
        try {
            level1 = Double.parseDouble(((TextView) findViewById(R.id.level1)).getText().toString());
            level2 = Double.parseDouble(((TextView) findViewById(R.id.level2)).getText().toString());
            level3 = Double.parseDouble(((TextView) findViewById(R.id.level3)).getText().toString());
            level4 = Double.parseDouble(((TextView) findViewById(R.id.level4)).getText().toString());
        } catch (Exception e) {
            Toast.makeText(this, "输入必须是数字", Toast.LENGTH_LONG).show();

            return;
        }

        XApplication.getServerInstance().managerGetResults(level1, level2, level3, level4, new AuthCallback() {
            @Override
            public void onFailureEx(Call call, IOException e) {
                showTextOnUIThread("网络问题！");
            }

            @Override
            public void onResponseEx(JSONObject data) throws IOException {
                if (data == null) {
                    showTextOnUIThread("服务器问题");
                } else if (data.getInteger("state") == 1) {
                    System.out.println(data);
                } else {
                    showTextOnUIThread(data.getString("message"));
                }
            }
        });
    }

    class UsersAdapter extends BaseAdapter {
        @Override
        public int getCount() {
            return 10;
        }

        @Override
        public Object getItem(int i) {
            return "";
        }

        @Override
        public long getItemId(int i) {
            return i;
        }

        @Override
        public View getView(int i, View convertView, ViewGroup viewGroup) {
            LayoutInflater inflater = getLayoutInflater();
            View view = convertView;
            UsersHolder viewHolder;
            if (convertView == null) {
                view = inflater.inflate(R.layout.item_user_detail, null);
                UsersHolder holder = new UsersHolder();
                holder.orderTextView =  view.findViewById(R.id.order);
                holder.coordinateTextView = view.findViewById(R.id.coordinate);
                holder.weightTextView = view.findViewById(R.id.weight);
                holder.scoreTextView = view.findViewById(R.id.score);
                view.setTag(holder);
                viewHolder = holder;
            }else{
                viewHolder = (UsersHolder) convertView.getTag();
            }

//            JSONObject object = data.getJSONObject(i);
//            viewHolder.userIdTextView.setText(object.getString("id"));
//            viewHolder.userNameTextView.setText(object.getString("username"));
//            viewHolder.departNameTextView.setText(object.getString("departname"));

            viewHolder.orderTextView.setText("1\n2\n3\n4\n5");
            viewHolder.coordinateTextView.setText("138.93456,32.765\n138.93456,32.765\n138.93456,32.765\n138.93456,32.765\n138.93456,32.765");
            viewHolder.weightTextView.setText("权重：60\n权重：60\n权重：60\n权重：60\n权重：60");
            viewHolder.scoreTextView.setText("得分：100\n得分：100\n得分：100\n得分：100\n得分：100");

            return view;
        }
    }

    class UsersHolder {
        TextView orderTextView;
        TextView coordinateTextView;
        TextView weightTextView;
        TextView scoreTextView;
    }
}
