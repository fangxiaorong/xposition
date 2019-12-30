package job.fscience.com.xposition;

import android.os.Bundle;
import android.view.View;
import android.widget.CompoundButton;
import android.widget.EditText;
import android.widget.Switch;
import android.widget.TextView;


import com.alibaba.fastjson.JSONObject;

import job.fscience.com.lib.BaseActivity;

public class PointInfoActivity extends BaseActivity {
    TextView xTextView;
    TextView yTextView;
    TextView maxDistanceTextView;
    TextView weightTextView;
    EditText startEditText;
    EditText endEditText;
    Switch startSwitch;
    Switch endSwitch;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_point_info);

        xTextView = (TextView) findViewById(R.id.x_text);
        yTextView = (TextView) findViewById(R.id.y_text);
        maxDistanceTextView = (TextView) findViewById(R.id.distance_text);
        weightTextView = (TextView) findViewById(R.id.weight_text);
        startEditText = (EditText) findViewById(R.id.start_text);
        endEditText = (EditText) findViewById(R.id.end_text);
        startSwitch = (Switch) findViewById(R.id.start_switch);
        endSwitch = (Switch) findViewById(R.id.end_switch);
        startSwitch.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton compoundButton, boolean b) {
                startEditText.setEnabled(b);
            }
        });
        endSwitch.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton compoundButton, boolean b) {
                endEditText.setEnabled(b);
            }
        });

        if (getIntent().hasExtra("info")) {
            JSONObject point = JSONObject.parseObject(getIntent().getStringExtra("info"));
            updateInfo(point);
            findViewById(R.id.delete_btn).setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {
//                    finishActivity();
                }
            });
        } else {
            findViewById(R.id.delete_btn).setVisibility(View.INVISIBLE);
        }
    }

    private void updateInfo (JSONObject point) {
        xTextView.setText(point.getString("x"));
        yTextView.setText(point.getString("y"));
        weightTextView.setText(point.getString("weight"));
        maxDistanceTextView.setText(point.getString("maxdistance"));

        if (point.getBoolean("senable")) {
            startSwitch.setChecked(true);
            startEditText.setText(point.getString("stime"));
            startEditText.setEnabled(true);
        } else {
            startSwitch.setChecked(false);
            startEditText.setText("");
            startEditText.setEnabled(false);
        }
        if (point.getBoolean("eenable")) {
            endSwitch.setChecked(true);
            endEditText.setText(point.getString("etime"));
            endEditText.setEnabled(true);
        } else {
            endSwitch.setChecked(false);
            endEditText.setText("");
            endEditText.setEnabled(false);
        }
    }
}
