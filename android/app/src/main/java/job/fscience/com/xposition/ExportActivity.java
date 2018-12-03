package job.fscience.com.xposition;

import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.TextView;
import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import job.fscience.com.lib.BaseActivity;
import job.fscience.com.lib.MacUtils;
import jxl.Workbook;
import jxl.write.Label;
import jxl.write.Number;
import jxl.write.WritableSheet;
import jxl.write.WritableWorkbook;
import org.apache.ftpserver.FtpServer;
import org.apache.ftpserver.FtpServerFactory;
import org.apache.ftpserver.ftplet.Authority;
import org.apache.ftpserver.listener.ListenerFactory;
import org.apache.ftpserver.usermanager.impl.BaseUser;
import org.apache.ftpserver.usermanager.impl.WritePermission;

import java.io.File;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Random;

public class ExportActivity extends BaseActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_export);

        findViewById(R.id.action).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if (server != null) {
                    server.stop();
                    server = null;
                    finish();
                }
            }
        });

        new Thread(){
            @Override
            public void run() {
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        ((TextView) findViewById(R.id.descript)).setText("等待文件写入");
                    }
                });
                writeFile();
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        ExportActivity.this.start();
                    }
                });
            }
        }.start();
    }

    private void writeFile() {
        String path = this.getFilesDir().getPath();

        try {
            JSONArray data = JSON.parseArray(getIntent().getStringExtra("data"));
            String examName = getIntent().getStringExtra("examName");
            Log.d("XX", data.toString());
            WritableWorkbook book = Workbook.createWorkbook(new File(path + "/" + examName + ".xls"));
            WritableSheet sheet = book.createSheet("sheet_one", 0);

            int maxCount = 0;

            for (int idx = 0; idx < data.size(); idx ++) {
                JSONObject user = data.getJSONObject(idx);

                JSONArray points = user.getJSONArray("points");
                int colCount = points.size() + 5;
                maxCount = colCount > maxCount ? colCount : maxCount;

                int row = idx + 1;
                Number orderNumber = new Number(0, row, row); sheet.addCell(orderNumber);
                Label userName = new Label(1, row, user.getString("username")); sheet.addCell(userName);
                Label departName = new Label(2, row, user.getString("departname")); sheet.addCell(departName);
                Label lineName = new Label(3, row, user.getString("linename")); sheet.addCell(lineName);
                Number score = new Number(4, row, user.getDouble("total_score")); sheet.addCell(score);
                for (int j = 0; j < points.size(); j ++) {
                    JSONObject point = points.getJSONObject(j);

                    Number xscore = new Number(5 + j, row, point.getDouble("score")); sheet.addCell(xscore);
                }
            }

            sheet.addCell(new Label(0, 0, "排名"));
            sheet.addCell(new Label(1, 0, "用户名"));
            sheet.addCell(new Label(2, 0, "单位名称"));
            sheet.addCell(new Label(3, 0, "考试线路"));
            sheet.addCell(new Label(4, 0, "总得分"));
            for (int idx = 5; idx < maxCount; idx ++) {
                sheet.addCell(new Label(idx, 0, "第" + (idx - 4) + "个考试点"));
            }

            book.write();
            book.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private String genPassword() {
        String code = "";
        Random rand = new Random();
        for(int a=0;a<6;a++){
            code+=rand.nextInt(10);
        }
        return code;
    }

    FtpServer server = null;
    public void start() {
        int port = 20000;
        String password = genPassword();

        try {
            String path = this.getFilesDir().getPath();

            FtpServerFactory serverFactory = new FtpServerFactory();
            //设置访问用户名和密码还有共享路径
            BaseUser baseUser = new BaseUser();
            baseUser.setName("admin");
            baseUser.setPassword(password);
            baseUser.setHomeDirectory(path);

            List<Authority> authorities = new ArrayList<>();
            authorities.add(new WritePermission());
            baseUser.setAuthorities(authorities);
            serverFactory.getUserManager().save(baseUser);

            ListenerFactory factory = new ListenerFactory();
            factory.setPort(port); //设置端口号 非ROOT不可使用1024以下的端口
            serverFactory.addListener("default", factory.createListener());

            server = serverFactory.createServer();
            server.start();

            String text = String.format("服务地址：ftp://%s:%d\n用户名: admin 密码: %s", MacUtils.getIpAddress(this), port, password);
            ((TextView) findViewById(R.id.descript)).setText(text);
        } catch (Exception e) {
            e.printStackTrace();
            ((TextView) findViewById(R.id.descript)).setText("服务器启动失败");
        }
    }

    @Override
    protected void onDestroy() {
        if (this.server != null) {
            this.server.stop();
            this.server = null;
        }
        super.onDestroy();
    }
}
