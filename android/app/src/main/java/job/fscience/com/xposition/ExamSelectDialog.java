package job.fscience.com.xposition;

import android.app.Dialog;
import android.content.Context;
import android.os.Bundle;
import android.support.annotation.NonNull;
import android.support.annotation.Nullable;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.ListView;
import android.widget.TextView;
import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;

public class ExamSelectDialog extends Dialog {
    JSONArray exams;
    int activeExamId;

    public ExamSelectDialog(@NonNull Context context, JSONArray exams, Integer activeExamId) {
        super(context);
        this.exams = exams;
        this.activeExamId = activeExamId;
    }

    public ExamSelectDialog(@NonNull Context context, int themeResId) {
        super(context, themeResId);
    }

    protected ExamSelectDialog(@NonNull Context context, boolean cancelable, @Nullable OnCancelListener cancelListener) {
        super(context, cancelable, cancelListener);
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.dialog_exam_select);

        ListView examListView = (ListView) findViewById(R.id.exam_list);
        ExamListAdapter adapter = new ExamListAdapter();
        examListView.setAdapter(adapter);
    }

    class ExamListAdapter extends BaseAdapter {

        @Override
        public int getCount() {
            if (exams == null) {
                return 0;
            }
            return exams.size();
        }

        @Override
        public Object getItem(int i) {
            if (exams == null) {
                return null;
            }
            return exams.get(i);
        }

        @Override
        public long getItemId(int i) {
            return i;
        }

        @Override
        public View getView(int i, View convertView, ViewGroup viewGroup) {
            Object object = getItem(i);
            if (object == null) {
                return null;
            }

            View view = convertView;
            ViewHolder holder;
            if (view == null) {
                view = getLayoutInflater().inflate(R.layout.item_exam_info, null);
                holder = new ViewHolder(view.findViewById(R.id.active_text), (TextView) view.findViewById(R.id.name_text), view.findViewById(R.id.current_text));
                view.setTag(holder);
            } else {
                holder = (ViewHolder) view.getTag();
            }

            JSONObject itemData = (JSONObject) object;
            if (itemData.getIntValue("id") == activeExamId) {
                holder.activateView.setVisibility(View.VISIBLE);
            } else {
                holder.activateView.setVisibility(View.INVISIBLE);
            }
            holder.nameView.setText(itemData.getString("name"));

            return view;
        }
    }

    class ViewHolder {
        View activateView;
        TextView nameView;
        View currentView;

        public ViewHolder(View activateView, TextView nameView, View currentView) {
            this.activateView = activateView;
            this.nameView = nameView;
            this.currentView = currentView;
        }
    }
}
