package job.fscience.com.xposition;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.EditText;
import android.widget.Toast;
import com.alibaba.fastjson.JSONObject;
import job.fscience.com.lib.AuthCallback;
import job.fscience.com.lib.BaseActivity;
import okhttp3.Call;

import java.io.IOException;

public class LoginActivity extends BaseActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

//        ((TextView)findViewById(R.id.user_id)).setText(MacUtils.getMobileMAC(this));
        findViewById(R.id.login).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                userLogin();
            }
        });

        checkLogin();
    }

    private void showTextOnUIThread(final String message) {
        this.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                Toast.makeText(LoginActivity.this, message, Toast.LENGTH_LONG).show();
            }
        });
    }

    ////
    private void checkLogin() {
        XApplication.getServerInstance().checkLogin(new AuthCallback() {
            @Override
            public void onFailureEx(Call call, IOException e) {
                showTextOnUIThread("网络问题");
            }

            @Override
            public void onResponseEx(JSONObject data) throws IOException {
                if (data == null) {
                    showTextOnUIThread("服务器问题");
                } else if (data.getInteger("state") == 1) {
                    XApplication.userInfo = data.getJSONObject("user_info");
                    getExam();
                } else {
                    userLogin();
                }
            }
        });
    }

    private void userLogin() {
        String userName = ((EditText) findViewById(R.id.nameText)).getText().toString().trim();
        String password = ((EditText) findViewById(R.id.passwordText)).getText().toString().trim();

        if (userName.equals("") || password.equals("")) {
            Toast.makeText(this, "用户名和密码不能为空", Toast.LENGTH_LONG).show();
            return;
        }

        XApplication.getServerInstance().managerLogin(userName, password, new AuthCallback() {
            @Override
            public void onFailureEx(Call call, IOException e) {
                showTextOnUIThread("网络问题");
            }

            @Override
            public void onResponseEx(JSONObject data) throws IOException {
                if (data == null) {
                    showTextOnUIThread("服务器问题");
                } else if (data.getInteger("state") == 1) {
                    XApplication.userInfo = data.getJSONObject("user_info");
                    getExam();
                } else {
                    showTextOnUIThread(data.getString("message"));
                }
            }
        });
    }

    private void getExam() {
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
                    XApplication.examInfo = data.getJSONObject("info");
                    Intent intent = new Intent(LoginActivity.this, MainActivity.class);
                    LoginActivity.this.startActivity(intent);
                    LoginActivity.this.finish();
                } else {
                    showTextOnUIThread(data.getString("message"));
                }
            }
        });
    }

//    private void getExamUsers() {
//        XApplication.getServerInstance().managerLogin(new AuthCallback() {
//            @Override
//            public void onFailureEx(Call call, IOException e) {
//                showTextOnUIThread("网络问题");
//            }
//
//            @Override
//            public void onResponseEx(JSONObject data) throws IOException {
//                if (data == null) {
//                    showTextOnUIThread("服务器问题");
//                } else if (data.getInteger("state") == 1) {
//                    Intent intent = new Intent(LoginActivity.this, MainActivity.class);
//                    LoginActivity.this.startActivity(intent);
//                    LoginActivity.this.finish();
//                } else {
//                    showTextOnUIThread("登录问题");
//                }
//            }
//        });
//    }
}
