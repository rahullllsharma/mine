import type { UserFormMode } from "../../customisedForm.types";
import ButtonIcon from "@/components/shared/button/icon/ButtonIcon";
import Modal from "@/components/shared/modal/Modal";
import IncludeInSummaryToggle from "@/components/dynamicForm/SummaryComponent/IncludeInSummaryToggle";
import style from "../createTemplateStyle.module.scss";

type PreviewCTASectionComponentType = {
  showAddSection?: boolean;
  isOpen: boolean;
  setIsOpen: (item: boolean) => void;
  onClickOfSection?: (item: boolean) => void;
  onClickOfDeletePage?: (item: boolean) => void;
  setQuestionModalOpen: () => void;
  setDataModalOpen: () => void;
  setComponentsModalOpen?: () => void;
  onToggleSummary?: (visibility: boolean) => void;
  mode: UserFormMode;
  includeSectionInSummaryToggle: boolean;
  showComponent?: boolean;
};

const DisplayDataOption = ({
  onClickAction,
}: {
  onClickAction: () => void;
}) => {
  return (
    <button className={style.IconButtonParent} onClick={onClickAction}>
      <svg
        width="60"
        height="60"
        viewBox="0 0 57 46"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <g clipPath="url(#clip0_1425_33014)">
          <path
            d="M44.9167 43.75H25.0833C23.5185 43.75 22.25 42.4815 22.25 40.9167V21.0833C22.25 19.5185 23.5185 18.25 25.0833 18.25H44.9167C46.4815 18.25 47.75 19.5185 47.75 21.0833V40.9167C47.75 42.4815 46.4815 43.75 44.9167 43.75ZM25.0833 21.0833V40.9167H44.9167V21.0833H25.0833ZM43.5 38.0833H26.5L30.75 32.4167L32.1667 33.8333L36.4167 28.1667L43.5 38.0833ZM30.0417 29.5833C28.8681 29.5833 27.9167 28.6319 27.9167 27.4583C27.9167 26.2847 28.8681 25.3333 30.0417 25.3333C31.2153 25.3333 32.1667 26.2847 32.1667 27.4583C32.1667 28.6319 31.2153 29.5833 30.0417 29.5833Z"
            fill="#3C4F55"
          />
          <path
            d="M2 3H26V7.64274H24.996C24.996 5.91966 24.6773 4.91453 24.0398 4.62735H16.1992V29.0376C16.4861 29.6758 17.49 29.9949 19.2112 29.9949V31H8.78884V29.9949C10.51 29.9949 11.5139 29.6758 11.8008 29.0376V4.62735H3.96016C3.32271 4.91453 3.00398 5.91966 3.00398 7.64274H2V3Z"
            fill="#3C4F55"
          />
        </g>
        <defs>
          <clipPath id="clip0_1425_33014">
            <rect width="57" height="46" fill="white" />
          </clipPath>
        </defs>
      </svg>
      <p>Display Data</p>
    </button>
  );
};

const AskQuestionOption = ({
  onClickAction,
}: {
  onClickAction: () => void;
}) => {
  return (
    <button className={style.IconButtonParent} onClick={onClickAction}>
      <svg
        width="60"
        height="60"
        viewBox="0 0 57 46"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M10.9689 26.1933C9.66813 24.8926 9.01188 23.6035 9.00016 22.3261C8.98844 21.0371 9.62711 19.7422 10.9162 18.4414L25.0841 4.29099C26.3732 3.00193 27.6623 2.36326 28.9513 2.37498C30.2404 2.38669 31.5353 3.04294 32.8361 4.34373L46.8986 18.4062C48.1994 19.707 48.8556 21.0078 48.8673 22.3086C48.8791 23.5976 48.2404 24.8808 46.9513 26.1582L32.8009 40.3261C31.5119 41.6152 30.2228 42.2539 28.9338 42.2422C27.6447 42.2304 26.3498 41.5742 25.049 40.2734L10.9689 26.1933ZM28.5646 26.0703C29.0216 26.0703 29.3791 25.9472 29.6369 25.7011C29.8947 25.4433 30.0236 25.1328 30.0236 24.7695C30.0236 24.7344 30.0236 24.6992 30.0236 24.664C30.0236 24.6172 30.0236 24.582 30.0236 24.5586C30.0236 24.0429 30.1759 23.6035 30.4806 23.2402C30.7853 22.8652 31.2541 22.4726 31.8869 22.0625C32.7658 21.4883 33.4865 20.8847 34.049 20.2519C34.6232 19.6191 34.9103 18.7578 34.9103 17.6679C34.9103 16.6601 34.6408 15.8164 34.1017 15.1367C33.5627 14.4453 32.8537 13.9238 31.9748 13.5722C31.1076 13.2207 30.1584 13.0449 29.1271 13.0449C27.5568 13.0449 26.2795 13.3554 25.2951 13.9765C24.3224 14.5976 23.7072 15.3301 23.4494 16.1738C23.4025 16.3144 23.3615 16.4609 23.3263 16.6133C23.3029 16.7656 23.2912 16.9179 23.2912 17.0703C23.2912 17.4687 23.4259 17.7793 23.6955 18.0019C23.965 18.2129 24.2521 18.3183 24.5568 18.3183C24.8615 18.3183 25.1193 18.2539 25.3302 18.125C25.5412 17.9844 25.7287 17.8086 25.8927 17.5976L26.2091 17.1582C26.4318 16.8066 26.6838 16.5078 26.965 16.2617C27.2463 16.0156 27.5568 15.8281 27.8966 15.6992C28.2365 15.5703 28.6056 15.5058 29.0041 15.5058C29.8244 15.5058 30.4806 15.7168 30.9728 16.1386C31.4767 16.5605 31.7287 17.1172 31.7287 17.8086C31.7287 18.4297 31.5353 18.9394 31.1486 19.3379C30.7619 19.7246 30.1701 20.1933 29.3732 20.7441C28.7287 21.2011 28.1896 21.6992 27.756 22.2383C27.3224 22.7773 27.1056 23.498 27.1056 24.4004C27.1056 24.4355 27.1056 24.4765 27.1056 24.5234C27.1056 24.5586 27.1056 24.5937 27.1056 24.6289C27.1056 25.5898 27.592 26.0703 28.5646 26.0703ZM28.5119 31.4668C29.0392 31.4668 29.4963 31.2851 29.883 30.9219C30.2814 30.5586 30.4806 30.1133 30.4806 29.5859C30.4806 29.0586 30.2873 28.6133 29.9005 28.25C29.5138 27.875 29.0509 27.6875 28.5119 27.6875C27.9845 27.6875 27.5275 27.875 27.1408 28.25C26.7541 28.625 26.5607 29.0703 26.5607 29.5859C26.5607 30.1133 26.7541 30.5586 27.1408 30.9219C27.5392 31.2851 27.9963 31.4668 28.5119 31.4668Z"
          fill="#3C4F55"
        />
      </svg>
      <p>Question</p>
    </button>
  );
};

const AddComponentOption = ({
  onClickAction,
}: {
  onClickAction: () => void;
}) => {
  return (
    <button className={style.IconButtonParent} onClick={onClickAction}>
      <svg
        width="60"
        height="60"
        viewBox="0 0 41 41"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M3.83594 20.8984C3.83594 21.7839 3.90104 22.6562 4.03125 23.5156C4.17448 24.362 4.36979 25.1823 4.61719 25.9766L1.57031 27.2656C1.23177 26.263 0.964844 25.2279 0.769531 24.1602C0.58724 23.0924 0.496094 22.0052 0.496094 20.8984C0.496094 19.7917 0.58724 18.7044 0.769531 17.6367C0.951823 16.569 1.21224 15.5339 1.55078 14.5312L4.61719 15.8203C4.36979 16.6146 4.17448 17.4414 4.03125 18.3008C3.90104 19.1471 3.83594 20.013 3.83594 20.8984ZM12.8203 6.09375C11.2708 6.90104 9.8776 7.92318 8.64062 9.16016C7.41667 10.3971 6.41406 11.7904 5.63281 13.3398L2.58594 12.0703C3.5625 10.1302 4.81901 8.39193 6.35547 6.85547C7.89193 5.31901 9.63021 4.0625 11.5703 3.08594L12.8203 6.09375ZM20.3984 4.29688C19.513 4.29688 18.6406 4.36849 17.7812 4.51172C16.9219 4.64193 16.0951 4.83724 15.3008 5.09766L14.0117 2.05078C15.0143 1.69922 16.0495 1.43229 17.1172 1.25C18.1979 1.06771 19.2917 0.976562 20.3984 0.976562C21.5052 0.976562 22.5924 1.06771 23.6602 1.25C24.7279 1.43229 25.763 1.69922 26.7656 2.05078L25.5156 5.09766C24.7083 4.83724 23.875 4.64193 23.0156 4.51172C22.1562 4.36849 21.2839 4.29688 20.3984 4.29688ZM35.2031 13.3203C34.4089 11.7578 33.3932 10.3646 32.1562 9.14062C30.9193 7.90365 29.526 6.88802 27.9766 6.09375L29.2266 3.06641C31.1536 4.04297 32.8919 5.30599 34.4414 6.85547C35.9909 8.39193 37.2539 10.1302 38.2305 12.0703L35.2031 13.3203ZM37.0195 20.8984C37.0195 20.013 36.9479 19.1406 36.8047 18.2812C36.6745 17.4219 36.4792 16.5951 36.2188 15.8008L39.2656 14.5117C39.6172 15.5143 39.8841 16.556 40.0664 17.6367C40.2487 18.7044 40.3398 19.7917 40.3398 20.8984C40.3398 22.0052 40.2487 23.099 40.0664 24.1797C39.8841 25.2474 39.6172 26.2826 39.2656 27.2852L36.2383 25.9961C36.4857 25.2018 36.6745 24.375 36.8047 23.5156C36.9479 22.6562 37.0195 21.7839 37.0195 20.8984ZM27.9766 35.6836C29.526 34.9023 30.9193 33.8932 32.1562 32.6562C33.4062 31.4193 34.4284 30.026 35.2227 28.4766L38.2109 29.7266C37.2474 31.6667 35.9909 33.4115 34.4414 34.9609C32.9049 36.4974 31.1667 37.7539 29.2266 38.7305L27.9766 35.6836ZM20.418 37.5C21.3034 37.5 22.1693 37.4284 23.0156 37.2852C23.862 37.1549 24.6888 36.9661 25.4961 36.7188L26.7656 39.7656C25.763 40.1042 24.7279 40.3646 23.6602 40.5469C22.6055 40.7292 21.5247 40.8203 20.418 40.8203C19.3112 40.8203 18.2174 40.7227 17.1367 40.5273C16.069 40.3451 15.0339 40.0846 14.0312 39.7461L15.3008 36.6992C16.0951 36.9596 16.9219 37.1549 17.7812 37.2852C18.6406 37.4284 19.5195 37.5 20.418 37.5ZM5.63281 28.4766C6.41406 30.026 7.41667 31.4193 8.64062 32.6562C9.8776 33.8802 11.2708 34.8828 12.8203 35.6641L11.5703 38.7109C9.64323 37.7344 7.91146 36.4779 6.375 34.9414C4.83854 33.4049 3.58203 31.6667 2.60547 29.7266L5.63281 28.4766ZM20.3789 34.5312C18.4909 34.5312 16.7201 34.1797 15.0664 33.4766C13.4258 32.7734 11.9805 31.8034 10.7305 30.5664C9.49349 29.3164 8.52344 27.8711 7.82031 26.2305C7.11719 24.5768 6.76562 22.7995 6.76562 20.8984C6.76562 18.9974 7.11068 17.2266 7.80078 15.5859C8.50391 13.9323 9.47396 12.4805 10.7109 11.2305C11.9609 9.98047 13.4062 9.01042 15.0469 8.32031C16.7005 7.61719 18.4714 7.26562 20.3594 7.26562C22.2604 7.26562 24.0312 7.61719 25.6719 8.32031C27.3255 9.02344 28.7773 10 30.0273 11.25C31.2773 12.487 32.2539 13.9323 32.957 15.5859C33.6602 17.2266 34.0117 18.9974 34.0117 20.8984C34.0247 22.7865 33.6797 24.5573 32.9766 26.2109C32.2734 27.8646 31.2969 29.3164 30.0469 30.5664C28.8099 31.8034 27.3646 32.7734 25.7109 33.4766C24.0573 34.1797 22.2799 34.5312 20.3789 34.5312Z"
          fill="#3C4F55"
        />
      </svg>
      <p>Component</p>
    </button>
  );
};

const PreviewCTASectionComponent = ({
  isOpen,
  setIsOpen,
  showAddSection = true,
  onClickOfSection,
  onClickOfDeletePage,
  setQuestionModalOpen,
  setDataModalOpen,
  setComponentsModalOpen,
  onToggleSummary,
  mode,
  includeSectionInSummaryToggle,
  showComponent = true,
}: PreviewCTASectionComponentType) => {
  const handleToggle = () => {
    onToggleSummary && onToggleSummary(!includeSectionInSummaryToggle);
  };

  const handleOnClickOfSection = (item: boolean) => {
    if (onClickOfSection) {
      onClickOfSection(item);
    }
  };

  return (
    <div className={`${style.previewComponentParent__ctaSection}`}>
      <ButtonIcon
        iconName="plus_square"
        onClick={() => {
          setIsOpen(true);
        }}
      />
      <ButtonIcon
        iconName="trash_empty"
        onClick={() => {
          if (onClickOfDeletePage) {
            onClickOfDeletePage(true);
          }
        }}
      />
      <IncludeInSummaryToggle
        includeSectionInSummaryToggle={includeSectionInSummaryToggle}
        handleToggle={handleToggle}
        mode={mode}
      />
      <Modal
        title={""}
        isOpen={isOpen}
        closeModal={() => {
          setIsOpen(false);
        }}
      >
        <div className={style.previewComponentParent__formElementsModal}>
          <div className={style.previewComponentParent__formElement}>
            <DisplayDataOption onClickAction={setDataModalOpen} />
          </div>

          <div className={style.previewComponentParent__formElement}>
            <AskQuestionOption onClickAction={() => setQuestionModalOpen()} />
          </div>
          {showComponent && (
            <div className={style.previewComponentParent__formElement}>
              <AddComponentOption
                onClickAction={() => {
                  if (setComponentsModalOpen) {
                    setComponentsModalOpen();
                  }
                }}
              />
            </div>
          )}
        </div>
        {showAddSection && (
          <>
            <hr className="mt-5 mb-2" />
            <div className="inline">
              <p className="text-black  inline">
                <span
                  className="cursor-pointer hover:text-brand-urbint-40"
                  onClick={() => {
                    setIsOpen(false);
                    handleOnClickOfSection(true);
                  }}
                >
                  Section
                </span>
              </p>
            </div>
          </>
        )}
      </Modal>
    </div>
  );
};

export default PreviewCTASectionComponent;

//"add_column" | "add_row" | "add_to_queue" | "adobe_xd" | "airplay" | "alarm_add" | "alarm" | "app_store" | "apple" | "arrowhead_outline" | "asterisk" | "attachment" | "bar_bottom" | "bar_chart_alt" | "bar_chart_circle" | "bar_chart_horizontal" | "bar_chart_square" | "bar_chart" | "bar_left" | "bar_right" | "bar_top" | "barcode" | "behance" | "black_lives_matter" | "bold" | "building" | "bulb" | "calendar_calendar" | "calendar_check" | "calendar_edit" | "calendar_event" | "calendar_minus" | "calendar_plus" | "calendar_week" | "calendar_x" | "calendar" | "calculator" | "camera" | "caret_down" | "caret_left" | "caret_right" | "caret_up" | "cast" | "chat_alt" | "chat" | "check_all_big" | "check_all" | "check_big" | "check_bold" | "check" | "checkbox_checked" | "checkbox_square" | "checkbox" | "chevron_big_down" | "chevron_big_left" | "chevron_big_right" | "chevron_big_up" | "chevron_down" | "chevron_duo_down" | "chevron_duo_left" | "chevron_duo_right" | "chevron_duo_up" | "chevron_left" | "chevron_right" | "chevron_up" | "circle" | "circle_check_outline" | "circle_check" | "circle_chevron_down" | "circle_chevron_left" | "circle_chevron_right" | "circle_chevron_up" | "circle_down" | "circle_left" | "circle_right" | "circle_up" | "clock" | "close_big" | "close_small" | "cloud_check" | "cloud_close" | "cloud_down" | "cloud_off" | "cloud_outline" | "cloud_up" | "cloud" | "code" | "coffee-togo" | "color" | "combine_cells" | "command" | "confused" | "cookie" | "coolicons" | "copy" | "credit_card_alt" | "credit_card" | "css3" | "cupcake" | "cylinder" | "dashboard_02" | "dashboard" | "data" | "delete_column" | "delete_row" | "devices" | "discord" | "dot_01_xs" | "dot_02_s" | "dot_03_m" | "dot_04_l" | "dot_05_xl" | "double_quotes_l" | "double_quotes_r" | "doughnut_chart" | "download_done" | "download" | "dribbble" | "dropbox" | "edit" | "error_outline" | "error" | "exit" | "expand" | "external_link" | "facebook" | "fast_forward" | "fast_rewind" | "Figma" | "file_archive" | "file_blank_fill" | "file_blank_outline" | "file_css" | "file_find" | "file_html" | "file_image" | "file_jpg" | "file_js" | "file_minus" | "file_new" | "file_pdf" | "file_png" | "file_svg" | "filter_applied" | "filter_off_outline" | "filter_off" | "filter_outline" | "filter" | "first_page" | "flag_fill" | "flag_outline" | "folder_minus" | "folder_open" | "folder_plus" | "folder" | "github" | "google" | "grid_big_round" | "grid_big" | "grid_horizontal_round" | "grid_horizontal" | "grid_round" | "grid_small_round" | "grid_small" | "grid_vertical_round" | "grid_vertical" | "grid" | "group_alt" | "group" | "hamburger" | "happy" | "heading_h1" | "heading_h2" | "heading_h3" | "heading_h4" | "heading_h5" | "heading_h6" | "heading" | "heart_fill" | "heart_outline" | "help_circle_outline" | "help_circle" | "help_questionmark" | "hide" | "history" | "home_alt_check" | "home_alt_fill" | "home_alt_minus" | "home_alt_outline" | "home_alt_plus" | "home_alt_x" | "home_check" | "home_fill" | "home_heart-1" | "home_heart" | "home_minus" | "home_outline" | "home_plus" | "home_x" | "html5" | "id_card" | "image_alt" | "image" | "info_circle_outline" | "info_circle" | "info_square_outline" | "info_square" | "instagram" | "invision" | "italic" | "javascript" | "label" | "laptop" | "last_page" | "layers_alt" | "layers_outline" | "layers" | "lightning" | "line_break" | "line_chart_down" | "line_chart_up" | "line_l" | "line_m" | "line_s" | "line_sx" | "line_xl" | "link_02" | "link" | "LinkedIn" | "linkpath" | "list_check" | "list_checklist_alt" | "list_checklist" | "list_minus" | "list_ol" | "list_plus" | "list_ul" | "loading" | "location_outline" | "location" | "lock" | "log_out" | "long_bottom_down" | "long_bottom_up" | "long_down" | "long_left" | "long_right" | "long_up_left" | "long_up_right" | "long_up" | "mail_open" | "mail" | "map" | "mention" | "menu_alt_01" | "menu_alt_02" | "menu_alt_03" | "menu_alt_04" | "menu_alt_05" | "menu_duo" | "message_check" | "message_circle" | "message_close" | "message_minus" | "message_plus_alt" | "message_plus" | "message_round" | "message_writing" | "message" | "messenger" | "minus_circle_outline" | "minus_circle" | "minus_square" | "minus" | "mobile_alt" | "mobile" | "monitor" | "moon" | "more_horizontal" | "more_vertical" | "move_horizontal" | "move_vertical" | "move" | "note" | "notification_active" | "notification_deactivated" | "notification_dot" | "notification_minus" | "notification_outline_dot" | "notification_outline_minus" | "notification_outline_plus" | "notification_outline" | "notification_plus" | "notification" | "off_close" | "off_outline_close" | "paragraph" | "path" | "pause_circle_filled" | "pause_circle_outline" | "paypal" | "phone_outline" | "phone" | "pie_chart_25" | "pie_chart_50" | "pie_chart_75" | "pie_chart_outline_25" | "pie_chart_outline" | "play_arrow" | "play_circle_filled" | "play_circle_outline" | "play_store" | "plus_circle_outline" | "plus_circle" | "plus_square" | "plus" | "polygonal_selector" | "projects_list" | "qr_code-1" | "qr_code" | "radio_filled" | "radio" | "reddit" | "redo" | "refresh_02" | "refresh" | "repeat" | "route" | "sad" | "search_small_minus" | "search_small_plus" | "search_small" | "search" | "select_multiple" | "settings_filled" | "settings_future" | "settings" | "share_outline" | "share" | "short_down" | "short_left" | "short_right" | "short_up" | "show" | "shrink" | "shuffle" | "single_quotes_l" | "single_quotes_r" | "Sketch" | "skip_next" | "skip_previous" | "slack" | "slider_01" | "slider_02" | "slider_03" | "small_long_down" | "small_long_left" | "small_long_right" | "small_long_up" | "snapchat" | "sort_down" | "sort_up" | "spectrum" | "spotify" | "stack_overflow" | "stopwatch" | "strikethrough" | "sub_left" | "sub_right" | "sun" | "table_add" | "table_delete" | "table" | "tablet" | "tag-outline" | "tag" | "target" | "tennis_match_alt" | "tennis_match" | "tennis" | "terminal" | "text_align_center" | "text_align_justify" | "text_align_left" | "text_align_right" | "thin_big_down" | "thin_big_left" | "thin_big_right" | "thin_big_up" | "thin_long_02_down" | "thin_long_02_left" | "thin_long_02_right" | "thin_long_02_up" | "thin_long_down" | "thin_long_left" | "thin_long_right" | "thin_long_up" | "ticket" | "tilde" | "transfer" | "trash_empty" | "trash_full" | "trello" | "trending_down" | "trending_up" | "twitter" | "underline" | "undo" | "unfold_less" | "unfold_more" | "unlink" | "unsplash" | "uploading" | "urbint" | "user_check" | "user_circle" | "user_close" | "user_heart" | "user_minus" | "user_pin" | "user_plus" | "user_square" | "user_voice" | "user" | "video" | "warning_outline" | "warning" | "window_check" | "window_close" | "window_code_block" | "window_sidebar" | "window_terminal" | "window" | "youtube";
