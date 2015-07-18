<?php

    function redirect($url, $statusCode = 303) {
        header('Location: ' . $url, true, $statusCode);
        die();
    }

    function endsWith($haystack, $needle) {
        // search forward starting from end minus needle length characters
        return $needle === "" || (($temp = strlen($haystack) - strlen($needle)) >= 0 && strpos($haystack, $needle, $temp) !== FALSE);
    }

    function append_line_to_file($line, $file) {
        $lines = file( $file, FILE_IGNORE_NEW_LINES);
        array_push( $lines, $line );
        file_put_contents( $file, implode("\n",$lines ) );
    }

?>
