package job.fscience.com.xposition1;

import android.content.Intent;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.widget.TextView;
import android.widget.Toast;
import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import job.fscience.com.lib.MacUtils;
import job.fscience.com.net.ServerRequest;
import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.Response;

import java.io.IOException;

public class LoginActivity extends AppCompatActivity {
    public static JSONObject userInfo = null;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        ((TextView)findViewById(R.id.user_id)).setText(MacUtils.getMobileMAC(this));
        findViewById(R.id.login).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                checkLogin();
            }
        });
    }

    private void checkLogin() {
        XApplication.getServerInstance().userLogin(MacUtils.getMobileMAC(this), new Callback() {
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
}
