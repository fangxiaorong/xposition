package job.fscience.com.xposition1;

import android.content.Intent;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.widget.*;
import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import job.fscience.com.lib.MacUtils;
import job.fscience.com.lib.SharedPreferencesHelper;
import job.fscience.com.net.ServerRequest;
import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.Response;

import javax.crypto.Mac;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class LoginActivity extends AppCompatActivity {
    public static JSONObject userInfo = null; // JSONObject.parseObject("{\"username\": \"username\", \"id\": 10}");
    private static SharedPreferencesHelper helper = null;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        helper = new SharedPreferencesHelper(this, "Login");

        String mac = (String) helper.getSharedPreference("mobile_mac", "");
        if (mac.equals("")) {
            mac = MacUtils.getSafeMobileMac(this);
            helper.put("mobile_mac", mac);
        }

        ((TextView)findViewById(R.id.user_id)).setText(mac.substring(0, 5) + mac.substring(mac.length() - 5));
        findViewById(R.id.login).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                userLogin();
            }
        });

        checkLogin();
    }

    private void getLines() {
        XApplication.getServerInstance().userLines(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                showTextOnUIThread("网络问题");
            }

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                final JSONObject object = ServerRequest.parseJSON(response);
                if (object == null) {
                    showTextOnUIThread("服务器错误");
                } else if (object.getInteger("state") == 1) {
                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            Spinner sp = (Spinner) findViewById(R.id.line);
                            JSONArray lines = object.getJSONArray("exam_line");
                            ArrayAdapter adapter = new ArrayAdapter(LoginActivity.this, R.layout.spinner_item_line_info, convertLineInfo(lines));
                            adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
                            sp.setAdapter(adapter);
                        }
                    });
                } else {
                    showTextOnUIThread(object.getString("message"));
                }
            }
        });
    }

    private void checkLogin() {
        XApplication.getServerInstance().checkLogin(MacUtils.getSafeMobileMac(this), new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                showTextOnUIThread("网络问题");
            }

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                JSONObject object = ServerRequest.parseJSON(response);
                if (object == null) {
                    showTextOnUIThread("服务器错误");
                } else if (object.getInteger("state") == 1) {
                    LoginActivity.userInfo = object.getJSONObject("user");
                    Intent intent = new Intent(LoginActivity.this, PositionActivity.class);
                    LoginActivity.this.startActivity(intent);
                    LoginActivity.this.finish();
                } else if (object.getInteger("state") == 10) {
                    getLines();
                }else {
                    showTextOnUIThread(object.getString("message"));
                }
            }
        });
    }

    private void userLogin() {
        String deviceId = MacUtils.getSafeMobileMac(this);
        String lineId = "" + ((LineInfo)((Spinner)findViewById(R.id.line)).getSelectedItem()).id;
        String username = ((EditText)findViewById(R.id.username)).getText().toString().trim();
        String departname = ((EditText)findViewById(R.id.departname)).getText().toString().trim();

        if (username.equals("") || departname.equals("")) {
            Toast.makeText(this, "用户名和单位名称不能为空！", Toast.LENGTH_LONG).show();
            return;
        }

        XApplication.getServerInstance().userLogin(deviceId, lineId, username, departname, new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                showTextOnUIThread("网络问题");
            }

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                JSONObject object = ServerRequest.parseJSON(response);
                if (object == null) {
                    showTextOnUIThread("服务器错误");
                } else if (object.getInteger("state") == 1) {
                    LoginActivity.userInfo = object.getJSONObject("user");
                    Intent intent = new Intent(LoginActivity.this, PositionActivity.class);
                    LoginActivity.this.startActivity(intent);
                    LoginActivity.this.finish();
                } else {
                    showTextOnUIThread(object.getString("message"));
                }
            }
        });
    }

    private void showTextOnUIThread(final String message) {
        this.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                Toast.makeText(LoginActivity.this, message, Toast.LENGTH_LONG).show();
            }
        });
    }

    class LineInfo {
        int id;
        String name;

        public LineInfo(int id, String name) {
            this.id = id;
            this.name = name;
        }

        @Override
        public String toString() {
            return name;
        }
    }

    private List<LineInfo> convertLineInfo(JSONArray lines) {
        ArrayList<LineInfo> result = new ArrayList<>();

        for (int idx = 0; idx < lines.size(); idx++) {
            JSONObject line = lines.getJSONObject(idx);

            result.add(new LineInfo(line.getInteger("id"), line.getString("name")));
        }

        return result;
    }
}
