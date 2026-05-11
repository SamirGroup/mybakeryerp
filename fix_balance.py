import re

with open('templates/manage_products.html', encoding='utf-8') as f:
    content = f.read()

# tab-day-balance div ni topib almashtirish
# Boshlanishi: '    <div id="tab-day-balance"'
# Tugashi: '    </div>\n\n    <!-- Edit product modal'

start_marker = '    <div id="tab-day-balance"'
end_marker = '    <!-- Edit product modal'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print(f"ERROR: start={start_idx}, end={end_idx}")
    exit(1)

print(f"Found: start={start_idx}, end={end_idx}")

new_block = '''    <div id="tab-day-balance" class="manage-tab-content grid-main">
        <div class="mg-card">
            <h3>Kunlik tayyor mahsulot</h3>
            <div class="mg-sub">Sana tanlang, qoldiqlarni ko\'ring yoki tahrirlang.</div>
            <form method="get" style="display:flex;gap:10px;flex-wrap:wrap;align-items:flex-end;margin-bottom:14px;">
                <div>
                    <label style="font-size:11px;font-weight:700;color:#7a6e62;text-transform:uppercase;">Sana</label>
                    <input type="date" name="balance_date" value="{{ balance_view_date|date:\'Y-m-d\' }}" class="form-control">
                </div>
                <button type="submit" class="btn btn-primary">Ko\'rish</button>
            </form>
            <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px;">
                <form method="POST" style="margin:0;">
                    {% csrf_token %}
                    <input type="hidden" name="action" value="close_inventory_day">
                    <input type="hidden" name="balance_date" value="{{ balance_view_date|date:\'Y-m-d\' }}">
                    <button type="submit" class="btn btn-primary" onclick="return confirm(\'Kun yakuni yozilsinmi?\')">Kun yakunini yozish</button>
                </form>
                <form method="POST" style="margin:0;">
                    {% csrf_token %}
                    <input type="hidden" name="action" value="carry_inventory_forward">
                    <input type="hidden" name="balance_date" value="{{ balance_view_date|date:\'Y-m-d\' }}">
                    <button type="submit" class="btn" style="background:#555;color:#fff;" onclick="return confirm(\'Keyingi kunga o\\\'tkazilsinmi?\')">Keyingi kunga o\'tkazish</button>
                </form>
            </div>
            <p class="mg-sub">Ko\'rilayotgan: <strong>{{ balance_view_date|date:"d.m.Y" }}</strong> &middot; Oldingi: {{ balance_prev_date|date:"d.m.Y" }}</p>
        </div>
        <div class="mg-card">
            <div class="section-head">
                <h3>Qoldiqlar jadvali</h3>
                <span class="count-pill">{{ balance_rows|length }} ta</span>
            </div>
            <div class="table-wrap">
                <table class="clean-table">
                    <thead>
                        <tr>
                            <th>Mahsulot</th>
                            <th>Fizik qoldiq</th>
                            <th>Kirish</th>
                            <th>Yakun</th>
                            <th>Vaqt</th>
                            <th>Amal</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for row in balance_rows %}
                        <tr>
                            <td><strong>{{ row.product.name }}</strong></td>
                            <td>{{ row.physical }}</td>
                            <td>{% if row.opening is not None %}{{ row.opening }}{% else %}&mdash;{% endif %}</td>
                            <td>{% if row.closing is not None %}<strong>{{ row.closing }}</strong>{% else %}&mdash;{% endif %}</td>
                            <td style="font-size:11px;color:#999;">{% if row.closed_at %}{{ row.closed_at|date:"d.m H:i" }}{% else %}&mdash;{% endif %}</td>
                            <td>
                                <button type="button" class="receive-btn" style="background:#d4a373;padding:5px 10px;font-size:11px;"
                                    onclick="openBalanceEditModal({{ row.product.id }},\'{{ row.product.name|escapejs }}\',{{ row.physical }},{% if row.opening is not None %}{{ row.opening }}{% else %}null{% endif %},{% if row.closing is not None %}{{ row.closing }}{% else %}null{% endif %})">Tahrirlash</button>
                            </td>
                        </tr>
                        {% empty %}
                        <tr><td colspan="6"><div class="empty-box">Mahsulotlar yo\'q.</div></td></tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- Balance Edit Modal -->
    <div id="balanceEditModal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.5);z-index:9999;align-items:center;justify-content:center;">
        <div style="background:white;padding:26px;border-radius:14px;max-width:420px;width:92%;">
            <h3 style="margin-top:0;" id="balanceEditTitle">Qoldiqni tahrirlash</h3>
            <form method="POST" id="balanceEditForm">
                {% csrf_token %}
                <input type="hidden" name="action" value="edit_balance_row">
                <input type="hidden" name="balance_date" value="{{ balance_view_date|date:\'Y-m-d\' }}">
                <input type="hidden" name="product_id" id="balEditProdId">
                <div class="form-group">
                    <label>Fizik qoldiq (ombordagi haqiqiy dona)</label>
                    <input type="number" name="physical" id="balEditPhysical" min="0" class="form-control" required>
                </div>
                <div class="form-group">
                    <label>Kirish qoldig\'i (opening)</label>
                    <input type="number" name="opening" id="balEditOpening" min="0" class="form-control">
                </div>
                <div class="form-group">
                    <label>Kun yakuni (closing)</label>
                    <input type="number" name="closing" id="balEditClosing" min="0" class="form-control">
                </div>
                <div style="display:flex;gap:10px;justify-content:flex-end;margin-top:16px;">
                    <button type="button" onclick="document.getElementById(\'balanceEditModal\').style.display=\'none\'" style="padding:10px 18px;border:1px solid #ccc;border-radius:8px;background:#f5f5f5;cursor:pointer;font-weight:700;">Bekor</button>
                    <button type="submit" style="padding:10px 18px;border:none;border-radius:8px;background:#d4a373;color:white;cursor:pointer;font-weight:700;">Saqlash</button>
                </div>
            </form>
        </div>
    </div>

    '''

new_content = content[:start_idx] + new_block + content[end_idx:]

with open('templates/manage_products.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("OK. New size:", len(new_content))
